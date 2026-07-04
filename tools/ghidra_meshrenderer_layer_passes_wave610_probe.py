#!/usr/bin/env python3
"""Validate Wave610 mesh renderer layer-pass Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave610-meshrenderer-layer-passes-0054d530"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_meshrenderer_layer_passes_wave610_2026-05-20.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
MESH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MeshRenderer.cpp" / "_index.md"
DXMESHVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXMeshVB.cpp" / "_index.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

ADDRESS = "0x0054d530"
NAME = "CMeshRenderer__RenderMeshWithLayerPasses"
SIGNATURE = (
    "void __thiscall CMeshRenderer__RenderMeshWithLayerPasses("
    "void * this, void * frame_provider, uint render_flags, "
    "void * unused_render_context, void * unused_transform_payload)"
)
COMMON_TAGS = {
    "static-reaudit",
    "meshrenderer-layer-passes-wave610",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
}
TARGET_TAGS = {
    "meshrenderer",
    "cdxmeshvb-layout",
    "layer-pass-render",
    "ret-0x10",
    "callsite-verified",
    "water-render-pass",
    "shader-state",
}
COMMENT_TOKENS = (
    "RET 0x10",
    "0x0054a4b6/0x0054b265",
    "four stack args after ECX",
    "caller's +0x138 CDXMeshVB-style render object",
    "render_flags uses bits 0x10/0x20/0x40",
    "not consumed by the current retail decompile",
    "DAT_0089c9c0/DAT_0089c9c4",
    "rebuild parity remain unproven",
)
OVERCLAIM_TOKENS = (
    "runtime behavior proven",
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


def require_log_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    values = parse_log_summary(path, failures)
    for key, expected_value in expected.items():
        if values.get(key) != expected_value:
            failures.append(f"{path.name} {key} mismatch: {values.get(key)} != {expected_value}")
    text = read_text(path)
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name} missing save-success report")
    for bad_token in (
        "LockException",
        "Function not found",
        "Input file not found",
        "Read-back signature mismatch",
        "Save blocked",
        "BAD:",
        "BADNAME:",
        "MISSING:",
    ):
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def check_logs(failures: list[str]) -> None:
    require_log_summary(
        BASE / "apply-dry.log",
        {"updated": 0, "skipped": 1, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "apply.log",
        {"updated": 1, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "apply-final-dry.log",
        {"updated": 0, "skipped": 1, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
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
    if "targets=1 missing=0" not in read_text(BASE / "post-instructions.log"):
        failures.append("post-instructions.log missing clean target summary")
    if "targets=1 dumped=1 missing=0 failed=0" not in read_text(BASE / "post-decompile.log"):
        failures.append("post-decompile.log missing clean decompile summary")
    if "targets=2 missing=0" not in read_text(BASE / "post-callsite-instructions.log"):
        failures.append("post-callsite-instructions.log missing clean callsite summary")


def check_metadata_and_tags(failures: list[str]) -> None:
    rows = read_tsv_rows(BASE / "post-metadata.tsv")
    if len(rows) != 1:
        failures.append(f"post-metadata row count mismatch: {len(rows)} != 1")
        return
    row = rows[0]
    if normalize_address(row["address"]) != ADDRESS:
        failures.append(f"metadata address mismatch: {row['address']} != {ADDRESS}")
    if row["name"] != NAME:
        failures.append(f"metadata name mismatch: {row['name']} != {NAME}")
    if row["signature"] != SIGNATURE:
        failures.append(f"metadata signature mismatch: {row['signature']} != {SIGNATURE}")
    if row["status"] != "OK":
        failures.append(f"metadata status mismatch: {row['status']}")
    require_tokens("metadata comment", row["comment"], COMMENT_TOKENS, failures)
    lowered = row["comment"].lower()
    for token in OVERCLAIM_TOKENS:
        if token in lowered:
            failures.append(f"metadata comment overclaims: {token}")

    tag_rows = read_tsv_rows(BASE / "post-tags.tsv")
    if len(tag_rows) != 1:
        failures.append(f"post-tags row count mismatch: {len(tag_rows)} != 1")
        return
    tag_row = tag_rows[0]
    actual_tags = set(filter(None, tag_row["tags"].split(";")))
    missing = (COMMON_TAGS | TARGET_TAGS) - actual_tags
    if normalize_address(tag_row["address"]) != ADDRESS:
        failures.append(f"tag address mismatch: {tag_row['address']} != {ADDRESS}")
    if tag_row["name"] != NAME:
        failures.append(f"tag name mismatch: {tag_row['name']} != {NAME}")
    if tag_row["status"] != "OK":
        failures.append(f"tag status mismatch: {tag_row['status']}")
    if missing:
        failures.append(f"missing tags: {sorted(missing)}")


def check_exports(failures: list[str]) -> None:
    xref_rows = read_tsv_rows(BASE / "post-xrefs.tsv")
    instruction_rows = read_tsv_rows(BASE / "post-instructions.tsv")
    target_instruction_rows = [row for row in instruction_rows if normalize_address(row.get("function_entry", "")) == ADDRESS]
    decompile_rows = read_tsv_rows(BASE / "post-decompile" / "index.tsv")
    callsite_rows = read_tsv_rows(BASE / "post-callsite-instructions.tsv")
    expected_counts = {
        "post-xrefs.tsv": (len(xref_rows), 2),
        "post-instructions.tsv": (len(instruction_rows), 2201),
        "target-function instructions": (len(target_instruction_rows), 763),
        "post-decompile/index.tsv": (len(decompile_rows), 1),
        "post-callsite-instructions.tsv": (len(callsite_rows), 114),
    }
    for label, (actual, expected) in expected_counts.items():
        if actual != expected:
            failures.append(f"{label} row count mismatch: {actual} != {expected}")

    xref_text = read_text(BASE / "post-xrefs.tsv")
    require_tokens("post-xrefs.tsv", xref_text, ("0054a4b6", "0054b265", "CMeshRenderer__RenderMeshCore"), failures)

    instruction_text = read_text(BASE / "post-instructions.tsv")
    require_tokens(
        "post-instructions.tsv",
        instruction_text,
        ("0x0054d530", "RET\t0x10", "0x0089c9c0", "CALL\t0x00513820", "PUSH\t0xb"),
        failures,
    )

    callsite_text = read_text(BASE / "post-callsite-instructions.tsv")
    require_tokens(
        "post-callsite-instructions.tsv",
        callsite_text,
        ("0x0054a4b6", "0x0054b265", "PUSH\tEDI", "PUSH\tEAX", "PUSH\tEDX", "PUSH\tECX"),
        failures,
    )

    decompile_text = read_text(BASE / "post-decompile" / "0054d530_CMeshRenderer__RenderMeshWithLayerPasses.c")
    require_tokens(
        "target decompile",
        decompile_text,
        (
            "void __thiscall",
            "frame_provider",
            "render_flags",
            "unused_render_context",
            "unused_transform_payload",
            "CVBufTexture__RenderModePass",
            "CWaterRenderSystem__ValidateVBufferAndMarkReady",
            "D3DStateCache__SetStateCached(1,0xb,1);",
        ),
        failures,
    )


def check_backup_and_queue(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    if backup.get("backupRoot") != "[maintainer-local-ghidra-backup-root]\\BEA_20260519-224655_post_wave610_meshrenderer_layer_passes_verified":
        failures.append(f"backup path mismatch: {backup.get('backupRoot')}")
    expected_backup = {
        "sourceFileCount": 19,
        "destFileCount": 19,
        "sourceBytes": 161418119,
        "destBytes": 161418119,
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
        "commentlessFunctionCount": 2968,
        "undefinedSignatureCount": 1301,
        "paramSignatureCount": 1059,
    }
    for key, expected_value in expected_quality.items():
        if quality.get(key) != expected_value:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected_value}")
    head = (queue.get("priorityQueues", {}).get("commentlessHighSignal") or [{}])[0]
    if head.get("address") != "0x0054e500" or head.get("name") != "DXPalletizer__InsertColor":
        failures.append(f"queue head mismatch: {head}")


def check_public_docs(failures: list[str]) -> None:
    for path in (
        PUBLIC_NOTE,
        PACKAGE_JSON,
        FUNCTION_INDEX,
        MESH_DOC,
        DXMESHVB_DOC,
        CAMPAIGN,
        BACKLOG,
        LEDGER,
        ATTEMPT_LOG,
        TRACKING,
    ):
        if not path.is_file():
            failures.append(f"missing expected file: {path}")
            return

    public_note = read_text(PUBLIC_NOTE)
    require_tokens(
        "public note",
        public_note,
        (
            "Ghidra Mesh Renderer Layer-Passes Wave610",
            SIGNATURE,
            "`2201` instruction rows",
            "`763` target-function instruction rows",
            "[maintainer-local-ghidra-backup-root]\\BEA_20260519-224655_post_wave610_meshrenderer_layer_passes_verified",
            "Next queue head: `0x0054e500 DXPalletizer__InsertColor`",
            "runtime rendering",
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
        (
            "test:ghidra-meshrenderer-layer-passes-wave610",
            "tools\\ghidra_meshrenderer_layer_passes_wave610_probe.py --check",
        ),
        failures,
    )

    for label, path in (
        ("functions index", FUNCTION_INDEX),
        ("MeshRenderer doc", MESH_DOC),
        ("DXMeshVB doc", DXMESHVB_DOC),
        ("campaign", CAMPAIGN),
        ("backlog", BACKLOG),
        ("ledger", LEDGER),
        ("attempt log", ATTEMPT_LOG),
    ):
        text = read_text(path)
        require_tokens(
            label,
            (
                text
            ),
            (
                "Wave610",
                NAME,
                "DXPalletizer__InsertColor",
                "2968",
                "commentless",
                "1059",
                "[maintainer-local-ghidra-backup-root]\\BEA_20260519-224655_post_wave610_meshrenderer_layer_passes_verified",
            ),
            failures,
        )

    tracking = read_json(TRACKING)
    if tracking.get("next_attempt_id") != 20266:
        failures.append(f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')} != 20266")
    if tracking.get("counters", {}).get("attempt_rows") != 20266:
        failures.append(f"tracking attempt_rows mismatch: {tracking.get('counters', {}).get('attempt_rows')} != 20266")


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
        print("Wave610 mesh renderer layer-pass probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave610 mesh renderer layer-pass probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
