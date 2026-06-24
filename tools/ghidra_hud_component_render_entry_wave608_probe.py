#!/usr/bin/env python3
"""Validate Wave608 HUD component render-entry Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave608-hud-component-render-entry-0054b800"
POST = BASE / "post"
CONTEXT = BASE / "context"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_hud_component_render_entry_wave608_2026-05-19.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
HUD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Hud.cpp" / "_index.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

ADDRESS = "0x0054b800"
NAME = "CHudComponent__RenderPassEntry"
SIGNATURE = "void __cdecl CHudComponent__RenderPassEntry(void * mesh_entry, void * hud_component)"
EXPECTED_TAGS = {
    "static-reaudit",
    "hud-component-render-entry-wave608",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
    "hud-component",
    "render-pass-entry",
    "direct-caller-verified",
    "cdecl",
    "ret-c3",
    "cvbuftexture",
    "2d-mesh-renderer",
}
COMMENT_TOKENS = (
    "direct caller CHudComponent__RenderPass",
    "owned mesh table at +0x160",
    "passes it first",
    "CHudComponent this pointer second",
    "plain cdecl with RET",
    "skips mesh types 2/4",
    "type 1 2D mesh triangles",
    "CVBufTexture SetVBFormat/SetIBFormat/AddVertices/AddIndices/Render",
    "DebugTrace for type 3 or unknown mesh types",
    "source-body identity",
    "runtime HUD behavior",
    "BEA patching",
    "rebuild parity remain unproven",
)
OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "source identity proven",
    "rebuild parity proven",
    "fully recovered",
    "fully reverse-engineered",
)


def normalize_address(address: str) -> str:
    value = address.strip().lower()
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


def require_log_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    values = parse_log_summary(path, failures)
    for key, expected_value in expected.items():
        if values.get(key) != expected_value:
            failures.append(f"{path.name} {key} mismatch: {values.get(key)} != {expected_value}")
    text = read_text(path)
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name} missing save-success report")
    for bad_token in ("LockException", "Function not found", "Input file not found", "Read-back signature mismatch", "Save blocked"):
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def check_logs(failures: list[str]) -> None:
    require_log_summary(BASE / "apply_dry.log", {"updated": 0, "skipped": 1, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply_apply.log", {"updated": 1, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply_final_dry.log", {"updated": 0, "skipped": 1, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)

    for log_name in (
        "ExportFunctionMetadataByAddress-targets.log",
        "ExportFunctionTagsByAddress-targets.log",
        "ExportXrefsForAddresses-targets.log",
        "ExportInstructionsAroundAddresses-targets.log",
        "ExportFunctionsByAddressDecompile-targets.log",
    ):
        text = read_text(POST / log_name)
        for bad_token in ("ERROR REPORT SCRIPT ERROR", "FileNotFoundException", "LockException", "BADADDR", "missing=1", "failed=1"):
            if bad_token in text:
                failures.append(f"{log_name} contains {bad_token}")
    context_log = read_text(CONTEXT / "ExportFunctionsByAddressDecompile-context.log")
    if "targets=1 dumped=1 missing=0 failed=0" not in context_log:
        failures.append("context decompile log missing clean summary")


def check_post_exports(failures: list[str]) -> None:
    metadata_rows = {normalize_address(row["address"]): row for row in read_tsv_rows(POST / "metadata_after.tsv")}
    tag_rows = {normalize_address(row["address"]): row for row in read_tsv_rows(POST / "tags_after.tsv")}
    if set(metadata_rows) != {ADDRESS}:
        failures.append(f"metadata address set mismatch: {sorted(metadata_rows)}")
    if set(tag_rows) != {ADDRESS}:
        failures.append(f"tag address set mismatch: {sorted(tag_rows)}")

    row = metadata_rows.get(ADDRESS)
    if row:
        if row["name"] != NAME:
            failures.append(f"name mismatch: {row['name']} != {NAME}")
        if row["signature"] != SIGNATURE:
            failures.append(f"signature mismatch: {row['signature']} != {SIGNATURE}")
        if row["status"] != "OK":
            failures.append(f"metadata status mismatch: {row['status']}")
        require_tokens("metadata comment", row["comment"], COMMENT_TOKENS, failures)
        lowered = row["comment"].lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"metadata comment overclaims: {token}")

    tag_row = tag_rows.get(ADDRESS)
    if tag_row:
        actual_tags = set(filter(None, tag_row["tags"].split(";")))
        missing = EXPECTED_TAGS - actual_tags
        if tag_row["name"] != NAME:
            failures.append(f"tag name mismatch: {tag_row['name']} != {NAME}")
        if tag_row["status"] != "OK":
            failures.append(f"tag status mismatch: {tag_row['status']}")
        if missing:
            failures.append(f"missing tags: {sorted(missing)}")

    expected_counts = {
        "post/xrefs_after.tsv": 1,
        "post/instructions_after.tsv": 512,
        "post/decomp_after/index.tsv": 1,
    }
    actual_counts = {
        "post/xrefs_after.tsv": len(read_tsv_rows(POST / "xrefs_after.tsv")),
        "post/instructions_after.tsv": len(read_tsv_rows(POST / "instructions_after.tsv")),
        "post/decomp_after/index.tsv": len(read_tsv_rows(POST / "decomp_after" / "index.tsv")),
    }
    for label, expected in expected_counts.items():
        if actual_counts[label] != expected:
            failures.append(f"{label} row count mismatch: {actual_counts[label]} != {expected}")


def check_xrefs_instructions_and_context(failures: list[str]) -> None:
    xref_text = read_text(POST / "xrefs_after.tsv")
    require_tokens(
        "xrefs_after",
        xref_text,
        ("0054b800", "004de88c", "004de860", "CHudComponent__RenderPass", "UNCONDITIONAL_CALL"),
        failures,
    )

    instruction_rows = read_tsv_rows(POST / "instructions_after.tsv")
    target_rows = [row for row in instruction_rows if row.get("function_name") == NAME]
    if len(target_rows) != 488:
        failures.append(f"target instruction row count mismatch: {len(target_rows)} != 488")
    if not target_rows or target_rows[-1].get("instruction_addr") != "0x0054bf77":
        failures.append("target instruction export does not end at 0x0054bf77")
    if target_rows and (target_rows[-1].get("mnemonic") != "RET" or target_rows[-1].get("bytes") != "c3"):
        failures.append("target instruction export does not end with RET c3")
    instruction_text = read_text(POST / "instructions_after.tsv")
    require_tokens(
        "instructions_after",
        instruction_text,
        (
            "0x0054b800",
            "0x0054bf77",
            "CALL\t0x00500540",
            "CALL\t0x00500590",
            "CALL\t0x00500a10",
            "CALL\t0x00500ac0",
            "CALL\t0x00500e70",
            "CALL\t0x0040c640",
            "RET\t",
        ),
        failures,
    )

    decompile_text = read_text(POST / "decomp_after" / "0054b800_CHudComponent__RenderPassEntry.c")
    require_tokens(
        "decomp_after",
        decompile_text,
        (
            "void __cdecl CHudComponent__RenderPassEntry(void *mesh_entry,void *hud_component)",
            "iVar5 = *(int *)((int)mesh_entry + 0x8c)",
            "CVBufTexture__SetVBFormat",
            "CVBufTexture__SetIBFormat",
            "CVBufTexture__AddVertices",
            "CVBufTexture__AddIndices",
            "CVBufTexture__Render",
            "DebugTrace",
        ),
        failures,
    )

    context_text = read_text(CONTEXT / "decomp_context" / "004de860_CHudComponent__RenderPass.c")
    require_tokens(
        "caller context",
        context_text,
        (
            "void __fastcall CHudComponent__RenderPass(void *this)",
            "CHudComponent__RenderPassEntry(*(int *)(*(int *)(iVar1 + 0x160) + iVar2 * 4),this);",
        ),
        failures,
    )


def check_backup_and_queue(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    if backup.get("backupPath") != "G:\\GhidraBackups\\BEA_20260519-214647_post_wave608_hud_component_render_entry_verified":
        failures.append(f"backup path mismatch: {backup.get('backupPath')}")
    expected_backup = {"fileCount": 19, "totalBytes": 161418119, "diffCount": 0}
    for key, expected_value in expected_backup.items():
        actual = backup.get(key)
        if isinstance(actual, float):
            actual = int(actual)
        if actual != expected_value:
            failures.append(f"backup {key} mismatch: {actual} != {expected_value}")

    queue = read_json(QUEUE_JSON)
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue totalFunctions mismatch: {queue.get('totalFunctions')} != 6093")
    quality = queue.get("qualitySignals", {})
    expected_quality = {
        "commentlessFunctionCount": 2976,
        "undefinedSignatureCount": 1304,
        "paramSignatureCount": 1064,
    }
    for key, expected_value in expected_quality.items():
        if quality.get(key) != expected_value:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected_value}")
    head = (queue.get("priorityQueues", {}).get("commentlessHighSignal") or [{}])[0]
    if head.get("address") != "0x0054bf80" or head.get("name") != "CDXMeshVB__ctor_like_0054bf80":
        failures.append(f"queue head mismatch: {head}")


def check_public_docs(failures: list[str]) -> None:
    expected_paths = (
        PUBLIC_NOTE,
        PACKAGE_JSON,
        FUNCTION_INDEX,
        HUD_DOC,
        CAMPAIGN,
        BACKLOG,
        LEDGER,
        ATTEMPT_LOG,
        TRACKING,
    )
    for path in expected_paths:
        if not path.is_file():
            failures.append(f"missing expected file: {path}")
            return

    public_note = read_text(PUBLIC_NOTE)
    require_tokens(
        "public note",
        public_note,
        (
            "Ghidra HUD Component Render Entry Wave608",
            SIGNATURE,
            "direct caller `CHudComponent__RenderPass`",
            "`512` instruction rows",
            "`488` target-function instruction rows",
            "G:\\GhidraBackups\\BEA_20260519-214647_post_wave608_hud_component_render_entry_verified",
            "Next queue head: `0x0054bf80 CDXMeshVB__ctor_like_0054bf80`",
            "runtime HUD behavior",
            "rebuild parity remain unproven",
        ),
        failures,
    )
    for token in OVERCLAIM_TOKENS:
        if token in public_note.lower():
            failures.append(f"public note overclaims: {token}")

    package_text = read_text(PACKAGE_JSON)
    require_tokens(
        "package.json",
        package_text,
        ("test:ghidra-hud-component-render-entry-wave608", "tools\\ghidra_hud_component_render_entry_wave608_probe.py --check"),
        failures,
    )

    for label, path in (
        ("functions index", FUNCTION_INDEX),
        ("HUD doc", HUD_DOC),
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
                "Wave608",
                "CHudComponent__RenderPassEntry",
                "0x0054b800",
                "0x0054bf80 CDXMeshVB__ctor_like_0054bf80",
                "2976",
                "commentless",
                "1064",
            ),
            failures,
        )

    tracking = read_json(TRACKING)
    if tracking.get("next_attempt_id") != 20264:
        failures.append(f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')} != 20264")
    if tracking.get("counters", {}).get("attempt_rows") != 20264:
        failures.append(f"tracking attempt_rows mismatch: {tracking.get('counters', {}).get('attempt_rows')} != 20264")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    failures: list[str] = []
    check_logs(failures)
    check_post_exports(failures)
    check_xrefs_instructions_and_context(failures)
    check_backup_and_queue(failures)
    check_public_docs(failures)

    if failures:
        print("Wave608 HUD component render-entry probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave608 HUD component render-entry probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
