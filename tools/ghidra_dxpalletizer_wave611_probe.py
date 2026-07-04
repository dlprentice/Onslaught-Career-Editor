#!/usr/bin/env python3
"""Validate Wave611 DXPalletizer Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave611-dxpalletizer-0054e500-0054f380"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_dxpalletizer_wave611_2026-05-20.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXPAL_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXPalletizer.cpp.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

SIGNATURES = {
    "0x0054e500": "void * __thiscall DXPalletizer__InsertColor(void * this, byte channel0, byte channel1, byte channel2, byte alpha_or_channel3, byte bit_depth)",
    "0x0054e670": "void __thiscall DXPalletizer__BuildPalette(void * this, uint * palette_words)",
    "0x0054e6e0": "int __thiscall DXPalletizer__AssignPaletteIndices(void * this, int * palette_counter, uint minimum_pixel_count)",
    "0x0054e790": "void __thiscall DXPalletizer__CollapseOctreeNode(void * this)",
    "0x0054e950": "void * __thiscall DXPalletizer__FreeOctreeNode(void * this, byte free_self)",
    "0x0054e9d0": "void __thiscall DXPalletizer__Palletize(void * this, void * source_rgba, int width, int height, uint requested_palette_size, void * out_indices_ref, void * out_palette_ref, int source_has_alpha, int allocate_outputs, int swizzle_output, int preserve_alpha, int expand_half_palette, int copy_palette_tiles)",
    "0x0054ef70": "byte __thiscall DXPalletizer__FindNearestColor(void * this, uint channel0, uint channel1, uint channel2, uint alpha_or_channel3)",
    "0x0054f090": "int __cdecl DXPalletizer__SwizzleBlock(int block_width, int block_height, void * src_block, void * dst_block)",
    "0x0054f380": "int __cdecl DXPalletizer__SwizzleTexture(uint width, int height, void * src_indices, void * dst_swizzled)",
}

NAMES = {
    "0x0054e500": "DXPalletizer__InsertColor",
    "0x0054e670": "DXPalletizer__BuildPalette",
    "0x0054e6e0": "DXPalletizer__AssignPaletteIndices",
    "0x0054e790": "DXPalletizer__CollapseOctreeNode",
    "0x0054e950": "DXPalletizer__FreeOctreeNode",
    "0x0054e9d0": "DXPalletizer__Palletize",
    "0x0054ef70": "DXPalletizer__FindNearestColor",
    "0x0054f090": "DXPalletizer__SwizzleBlock",
    "0x0054f380": "DXPalletizer__SwizzleTexture",
}

COMMON_TAGS = {
    "static-reaudit",
    "dxpalletizer-wave611",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
    "dxpalletizer",
    "callsite-verified",
}

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime texture output proven",
    "source identity proven",
    "rebuild parity proven",
    "fully recovered",
    "fully reverse-engineered",
)


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_tsv_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require_tokens(label: str, text: str, tokens: tuple[str, ...] | set[str], failures: list[str]) -> None:
    normalized = text.replace("\\\\", "\\")
    for token in tokens:
        if token not in normalized:
            failures.append(f"{label} missing token: {token}")


def parse_log_summary(path: Path, failures: list[str]) -> dict[str, int]:
    text = read_text(path)
    match = re.search(r"SUMMARY:\s+([^\r\n]+)", text)
    if not match:
        failures.append(f"{path.name} missing SUMMARY")
        return {}
    return {key: int(value) for key, value in re.findall(r"([a-z_]+)=([0-9]+)", match.group(1))}


def require_log_summary(path: Path, expected: dict[str, int], failures: list[str], *, allow_errors: bool = False) -> None:
    values = parse_log_summary(path, failures)
    for key, expected_value in expected.items():
        if values.get(key) != expected_value:
            failures.append(f"{path.name} {key} mismatch: {values.get(key)} != {expected_value}")
    text = read_text(path)
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name} missing save-success report")
    bad_tokens = ("LockException", "Function not found", "Input file not found", "BADADDR", "MISSING:")
    if not allow_errors:
        bad_tokens += ("ERROR REPORT SCRIPT ERROR", "BAD:", "BADNAME:", "Read-back signature mismatch")
    for bad_token in bad_tokens:
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def check_logs(failures: list[str]) -> None:
    require_log_summary(
        BASE / "apply-dry.log",
        {"updated": 0, "skipped": 9, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "apply-final-dry.log",
        {"updated": 0, "skipped": 9, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "apply.log",
        {"updated": 0, "skipped": 9, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "apply-initial-thiscall-mismatch.log",
        {"updated": 2, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 7},
        failures,
        allow_errors=True,
    )
    require_log_summary(
        BASE / "apply-corrected-this-pointer-mismatch.log",
        {"updated": 6, "skipped": 2, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 1},
        failures,
        allow_errors=True,
    )
    initial = read_text(BASE / "apply-initial-thiscall-mismatch.log")
    require_tokens(
        "initial mismatch log",
        initial,
        ("Read-back signature mismatch", "void * this, void * node", "SUMMARY: updated=2 skipped=0 renamed=0 would_rename=0 missing=0 bad=7"),
        failures,
    )
    corrected = read_text(BASE / "apply-corrected-this-pointer-mismatch.log")
    require_tokens(
        "corrected mismatch log",
        corrected,
        ("Read-back signature mismatch", "DXPalletizer__FindNearestColor", "SUMMARY: updated=6 skipped=2 renamed=0 would_rename=0 missing=0 bad=1"),
        failures,
    )

    for log_name in (
        "post-metadata.log",
        "post-tags.log",
        "post-xrefs.log",
        "post-instructions.log",
        "post-decompile.log",
        "post-callsite-instructions.log",
    ):
        text = read_text(BASE / log_name)
        for bad_token in ("ERROR REPORT SCRIPT ERROR", "FileNotFoundException", "LockException", "BADADDR", "missing=1", "failed=1"):
            if bad_token in text:
                failures.append(f"{log_name} contains {bad_token}")
    if "targets=9 missing=0" not in read_text(BASE / "post-instructions.log"):
        failures.append("post-instructions.log missing clean target summary")
    if "targets=9 dumped=9 missing=0 failed=0" not in read_text(BASE / "post-decompile.log"):
        failures.append("post-decompile.log missing clean decompile summary")
    if "targets=15 missing=0" not in read_text(BASE / "post-callsite-instructions.log"):
        failures.append("post-callsite-instructions.log missing clean callsite summary")


def check_metadata_and_tags(failures: list[str]) -> None:
    rows = read_tsv_rows(BASE / "post-metadata.tsv")
    if len(rows) != len(SIGNATURES):
        failures.append(f"post-metadata row count mismatch: {len(rows)} != {len(SIGNATURES)}")
        return
    for row in rows:
        address = normalize_address(row["address"])
        if address not in SIGNATURES:
            failures.append(f"unexpected metadata address: {row['address']}")
            continue
        if row["name"] != NAMES[address]:
            failures.append(f"metadata name mismatch for {address}: {row['name']} != {NAMES[address]}")
        if row["signature"] != SIGNATURES[address]:
            failures.append(f"metadata signature mismatch for {address}: {row['signature']} != {SIGNATURES[address]}")
        if row["status"] != "OK":
            failures.append(f"metadata status mismatch for {address}: {row['status']}")
        require_tokens("metadata comment", row["comment"], ("Wave611", "Static retail decompile/instruction/xref evidence only", "rebuild parity remain unproven"), failures)
        lowered = row["comment"].lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"metadata comment overclaims for {address}: {token}")

    tag_rows = read_tsv_rows(BASE / "post-tags.tsv")
    if len(tag_rows) != len(SIGNATURES):
        failures.append(f"post-tags row count mismatch: {len(tag_rows)} != {len(SIGNATURES)}")
        return
    for row in tag_rows:
        address = normalize_address(row["address"])
        tags = set(filter(None, row["tags"].split(";")))
        missing = COMMON_TAGS - tags
        if missing:
            failures.append(f"missing common tags for {address}: {sorted(missing)}")
        if address in ("0x0054f090", "0x0054f380") and not {"texture-swizzle", "morton-order", "cdecl-helper"}.issubset(tags):
            failures.append(f"missing swizzle tags for {address}: {sorted(tags)}")
        if address in ("0x0054e500", "0x0054e670", "0x0054e6e0", "0x0054e790", "0x0054e950", "0x0054e9d0", "0x0054ef70") and "octree-palette" not in tags:
            failures.append(f"missing octree-palette tag for {address}")


def check_exports(failures: list[str]) -> None:
    counts = {
        "post-xrefs.tsv": (len(read_tsv_rows(BASE / "post-xrefs.tsv")), 15),
        "post-instructions.tsv": (len(read_tsv_rows(BASE / "post-instructions.tsv")), 2349),
        "post-decompile/index.tsv": (len(read_tsv_rows(BASE / "post-decompile" / "index.tsv")), 9),
        "post-callsite-instructions.tsv": (len(read_tsv_rows(BASE / "post-callsite-instructions.tsv")), 435),
    }
    for label, (actual, expected) in counts.items():
        if actual != expected:
            failures.append(f"{label} row count mismatch: {actual} != {expected}")

    require_tokens(
        "post-xrefs.tsv",
        read_text(BASE / "post-xrefs.tsv"),
        ("005479a6", "CDXEngine__BuildLandscapeTextureCache", "0054eb41", "0054ecc0", "0054f50f"),
        failures,
    )
    require_tokens(
        "post-instructions.tsv",
        read_text(BASE / "post-instructions.tsv"),
        ("0x0054e500", "CALL\t0x005490e0", "0x0054f380", "CALL\t0x0054f090"),
        failures,
    )
    require_tokens(
        "post-callsite-instructions.tsv",
        read_text(BASE / "post-callsite-instructions.tsv"),
        ("0x005479a6", "PUSH\t0x100", "CALL\t0x0054e9d0", "0x0054ecc0", "CALL\t0x0054f380"),
        failures,
    )

    decompile_root = BASE / "post-decompile"
    decompile_blob = "\n".join(path.read_text(encoding="utf-8-sig") for path in sorted(decompile_root.glob("0054*.c")))
    require_tokens(
        "post-decompile",
        decompile_blob,
        (
            "DXPalletizer__InsertColor",
            "DXPalletizer__AssignPaletteIndices",
            "DXPalletizer__CollapseOctreeNode",
            "DXPalletizer__FindNearestColor",
            "DXPalletizer__SwizzleTexture(width,height",
            "DAT_00651ce0",
            "DAT_00651760",
            "DAT_00651960",
            "DAT_00651c60",
            "DAT_006fbe44/DAT_006fbe54",
        ),
        failures,
    )


def check_backup_and_queue(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    if backup.get("backupRoot") != "[maintainer-local-ghidra-backup-root]\\BEA_20260519-231515_post_wave611_dxpalletizer_verified":
        failures.append(f"backup path mismatch: {backup.get('backupRoot')}")
    expected_backup = {
        "sourceFileCount": 19,
        "destFileCount": 19,
        "sourceBytes": 161549191,
        "destBytes": 161549191,
        "diffCount": 0,
    }
    for key, expected_value in expected_backup.items():
        actual = backup.get(key)
        if isinstance(actual, float):
            actual = int(actual)
        if actual != expected_value:
            failures.append(f"backup {key} mismatch: {actual} != {expected_value}")

    queue = read_json(QUEUE_JSON)
    if queue.get("status") != "PASS":
        failures.append(f"queue status mismatch: {queue.get('status')}")
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue totalFunctions mismatch: {queue.get('totalFunctions')} != 6093")
    quality = queue.get("qualitySignals", {})
    expected_quality = {
        "commentlessFunctionCount": 2959,
        "undefinedSignatureCount": 1292,
        "paramSignatureCount": 1059,
    }
    for key, expected_value in expected_quality.items():
        if quality.get(key) != expected_value:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected_value}")
    head = (queue.get("priorityQueues", {}).get("commentlessHighSignal") or [{}])[0]
    if head.get("address") != "0x0054f6e0" or head.get("name") != "CDXEngine__ShutdownParticleSystemBundle":
        failures.append(f"queue head mismatch: {head}")


def check_public_docs(failures: list[str]) -> None:
    for path in (PUBLIC_NOTE, PACKAGE_JSON, FUNCTION_INDEX, DXPAL_DOC, CAMPAIGN, BACKLOG, LEDGER, ATTEMPT_LOG, TRACKING):
        if not path.is_file():
            failures.append(f"missing expected file: {path}")
            return

    note = read_text(PUBLIC_NOTE)
    require_tokens(
        "public note",
        note,
        (
            "Ghidra DXPalletizer Wave611",
            "DXPalletizer__Palletize",
            "`9` metadata rows",
            "`15` xref rows",
            "`2349` instruction rows",
            "`435` callsite instruction rows",
            "[maintainer-local-ghidra-backup-root]\\BEA_20260519-231515_post_wave611_dxpalletizer_verified",
            "Next queue head: `0x0054f6e0 CDXEngine__ShutdownParticleSystemBundle`",
            "runtime texture output",
            "rebuild parity remain unproven",
        ),
        failures,
    )
    for token in OVERCLAIM_TOKENS:
        if token in note.lower():
            failures.append(f"public note overclaims: {token}")

    package_text = read_text(PACKAGE_JSON)
    require_tokens(
        "package.json",
        package_text,
        ("test:ghidra-dxpalletizer-wave611", "tools\\ghidra_dxpalletizer_wave611_probe.py --check"),
        failures,
    )

    for label, path in (
        ("functions index", FUNCTION_INDEX),
        ("DXPalletizer doc", DXPAL_DOC),
        ("campaign", CAMPAIGN),
        ("backlog", BACKLOG),
        ("ledger", LEDGER),
        ("attempt log", ATTEMPT_LOG),
    ):
        text = read_text(path)
        require_tokens(
            label,
            text,
            (
                "Wave611",
                "DXPalletizer__Palletize",
                "DXPalletizer__SwizzleTexture",
                "2959",
                "1292",
                "CDXEngine__ShutdownParticleSystemBundle",
                "[maintainer-local-ghidra-backup-root]\\BEA_20260519-231515_post_wave611_dxpalletizer_verified",
            ),
            failures,
        )

    tracking = read_json(TRACKING)
    if tracking.get("next_attempt_id") != 20267:
        failures.append(f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')} != 20267")
    if tracking.get("counters", {}).get("attempt_rows") != 20267:
        failures.append(f"tracking attempt_rows mismatch: {tracking.get('counters', {}).get('attempt_rows')} != 20267")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    failures: list[str] = []
    check_logs(failures)
    check_metadata_and_tags(failures)
    check_exports(failures)
    check_backup_and_queue(failures)
    check_public_docs(failures)

    if failures:
        print("Wave611 DXPalletizer probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave611 DXPalletizer probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
