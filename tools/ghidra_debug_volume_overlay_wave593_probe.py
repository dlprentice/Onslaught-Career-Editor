#!/usr/bin/env python3
"""Validate Wave593 debug-volume overlay Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave593-debug-volume-overlay-0053d760"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_debug_volume_overlay_wave593_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
THING_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "thing.cpp" / "_index.md"
MESH_RENDERER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MeshRenderer.cpp" / "_index.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
BACKUP_SUMMARY = BASE / "wave593_backup_summary.json"

TARGET = "0x0053d760"
TARGET_NAME = "CThing__RenderDebugVolumeOverlay"
SIGNATURE = (
    "void __stdcall CThing__RenderDebugVolumeOverlay(uint color_argb, void * half_extents_vec3, "
    "void * center_vec3, float m00, float m01, float m02, float m03_unused, float m10, "
    "float m11, float m12, float m13_unused, float m20, float m21, float m22, "
    "float m23_unused, void * texture_or_material)"
)

TAGS = {
    "static-reaudit",
    "debug-volume-overlay-wave593",
    "retail-binary-evidence",
    "cthing",
    "debug-render",
    "ret-0x40",
    "signature-corrected",
    "comment-hardened",
    "debug-volume",
    "cvbuftexture",
    "render-state",
    "mesh-renderer-xref",
    "cthing-xref",
    "mapwho-xref",
    "debug-marker-xref",
}

COMMENT_TOKENS = (
    "RET 0x40",
    "CDebugMarkers__Render",
    "CMapWho__DebugDrawSector",
    "CMeshRenderer__RenderMesh",
    "CThing__DrawDebugCuboid",
    "color_argb",
    "half_extents_vec3",
    "center_vec3",
    "twelve copied transform dwords",
    "texture_or_material",
    "render states 0x1b/0x13/0x14",
    "CVBufTexture",
    "six faces",
    "Static retail evidence only",
    "runtime debug-render behavior",
    "rebuild parity remain unproven",
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "source identity proven",
    "rebuild parity proven",
    "fully recovered",
    "fully re'ed",
    "fully reverse-engineered",
)


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
    match = re.search(r"SUMMARY\s+([^\r\n]+)", text)
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
    require_log_summary(
        BASE / "logs" / "wave593_apply_dry.log",
        {"updated": 0, "skipped": 1, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "logs" / "wave593_apply.log",
        {"updated": 1, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "logs" / "wave593_apply_final_dry.log",
        {"updated": 0, "skipped": 1, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )


def check_post_exports(failures: list[str]) -> None:
    metadata_rows = read_tsv_rows(BASE / "post" / "metadata.tsv")
    tag_rows = read_tsv_rows(BASE / "post" / "tags.tsv")
    if len(metadata_rows) != 1:
        failures.append(f"metadata row count mismatch: {len(metadata_rows)}")
    if len(tag_rows) != 1:
        failures.append(f"tag row count mismatch: {len(tag_rows)}")

    if metadata_rows:
        row = metadata_rows[0]
        if normalize_address(row["address"]) != TARGET:
            failures.append(f"metadata address mismatch: {row['address']}")
        if row["name"] != TARGET_NAME:
            failures.append(f"name mismatch: {row['name']} != {TARGET_NAME}")
        if row["signature"] != SIGNATURE:
            failures.append(f"signature mismatch: {row['signature']} != {SIGNATURE}")
        if row["status"] != "OK":
            failures.append(f"metadata status mismatch: {row['status']}")
        require_tokens("metadata comment", row["comment"], COMMENT_TOKENS, failures)
        lowered = row["comment"].lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"metadata comment overclaims: {token}")

    if tag_rows:
        row = tag_rows[0]
        actual_tags = set(filter(None, row["tags"].split(";")))
        missing = TAGS - actual_tags
        if normalize_address(row["address"]) != TARGET:
            failures.append(f"tags address mismatch: {row['address']}")
        if row["name"] != TARGET_NAME:
            failures.append(f"tags name mismatch: {row['name']}")
        if row["status"] != "OK":
            failures.append(f"tags status mismatch: {row['status']}")
        if missing:
            failures.append(f"missing tags: {sorted(missing)}")

    expected_counts = {
        "xrefs.tsv": 10,
        "instructions.tsv": 1701,
        "decompile/index.tsv": 1,
        "decompile/callers/index.tsv": 4,
        "callsite_instructions.tsv": 490,
        "proof_instructions.tsv": 446,
    }
    actual_counts = {
        "xrefs.tsv": row_count(BASE / "post" / "xrefs.tsv"),
        "instructions.tsv": row_count(BASE / "post" / "instructions.tsv"),
        "decompile/index.tsv": row_count(BASE / "post" / "decompile" / "index.tsv"),
        "decompile/callers/index.tsv": row_count(BASE / "post" / "decompile" / "callers" / "index.tsv"),
        "callsite_instructions.tsv": row_count(BASE / "post" / "callsite_instructions.tsv"),
        "proof_instructions.tsv": row_count(BASE / "post" / "proof_instructions.tsv"),
    }
    for label, expected in expected_counts.items():
        if actual_counts[label] != expected:
            failures.append(f"post {label} row count mismatch: {actual_counts[label]} != {expected}")


def check_xrefs(failures: list[str]) -> None:
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
    expected = {
        (TARGET, TARGET_NAME, "0x0044207c", "0x00441ea0", "CDebugMarkers__Render", "UNCONDITIONAL_CALL"),
        (TARGET, TARGET_NAME, "0x0049293c", "0x00492860", "CMapWho__DebugDrawSector", "UNCONDITIONAL_CALL"),
        (TARGET, TARGET_NAME, "0x004b6b8e", "0x004b6350", "CMeshRenderer__RenderMesh", "UNCONDITIONAL_CALL"),
        (TARGET, TARGET_NAME, "0x004f388b", "0x004f37c0", "CThing__DrawDebugCuboid", "UNCONDITIONAL_CALL"),
        (TARGET, TARGET_NAME, "0x004f3924", "0x004f37c0", "CThing__DrawDebugCuboid", "UNCONDITIONAL_CALL"),
    }
    missing = expected - xrefs
    if missing:
        failures.append(f"missing expected xrefs: {sorted(missing)}")


def instruction_index(paths: list[Path]) -> set[tuple[str, str, str, str]]:
    rows: list[dict[str, str]] = []
    for path in paths:
        rows.extend(read_tsv_rows(path))
    return {
        (
            normalize_address(row["instruction_addr"]),
            row["function_name"],
            row["mnemonic"],
            row["operands"],
        )
        for row in rows
    }


def check_instruction_evidence(failures: list[str]) -> None:
    instructions = instruction_index(
        [
            BASE / "post" / "instructions.tsv",
            BASE / "post" / "proof_instructions.tsv",
            BASE / "post" / "callsite_instructions.tsv",
        ]
    )
    expected = {
        ("0x0053d8c7", TARGET_NAME, "JMP", "dword ptr [EDI*0x4 + 0x53df20]"),
        ("0x0053df1a", TARGET_NAME, "RET", "0x40"),
        ("0x0053d894", TARGET_NAME, "CALL", "0x00500540"),
        ("0x0053d8a6", TARGET_NAME, "CALL", "0x00500590"),
        ("0x0053de2d", TARGET_NAME, "CALL", "0x00500a10"),
        ("0x0053debf", TARGET_NAME, "CALL", "0x00500ac0"),
        ("0x0053ded6", TARGET_NAME, "CALL", "0x00500e70"),
        ("0x0053dee1", TARGET_NAME, "CALL", "0x00501310"),
        ("0x0053deef", TARGET_NAME, "CALL", "0x00513bc0"),
        ("0x0053df0b", TARGET_NAME, "CALL", "0x00550d50"),
        ("0x0044205f", "CDebugMarkers__Render", "MOVSD.REP", "ES:EDI, ESI"),
        ("0x0049292e", "CMapWho__DebugDrawSector", "MOVSD.REP", "ES:EDI, ESI"),
        ("0x004b6b80", "CMeshRenderer__RenderMesh", "MOVSD.REP", "ES:EDI, ESI"),
        ("0x004f3869", "CThing__DrawDebugCuboid", "PUSH", "0xff00ff00"),
        ("0x004f3905", "CThing__DrawDebugCuboid", "PUSH", "-0x1"),
    }
    missing = expected - instructions
    if missing:
        failures.append(f"missing instruction evidence: {sorted(missing)}")


def check_queue_and_backup(failures: list[str]) -> None:
    queue = json.loads(read_text(QUEUE_JSON))
    expected = {
        "totalFunctions": 6093,
        ("qualitySignals", "commentlessFunctionCount"): 3060,
        ("qualitySignals", "undefinedSignatureCount"): 1347,
        ("qualitySignals", "paramSignatureCount"): 1100,
    }
    for key, expected_value in expected.items():
        if isinstance(key, tuple):
            actual = queue[key[0]][key[1]]
            label = ".".join(key)
        else:
            actual = queue[key]
            label = key
        if actual != expected_value:
            failures.append(f"queue {label} mismatch: {actual} != {expected_value}")
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    if head["address"] != "0x0053f040" or head["name"] != "CVBufTexture__SetStateCacheModeByFlag":
        failures.append(f"queue head mismatch: {head}")

    backup = json.loads(read_text(BACKUP_SUMMARY))
    expected_backup = {
        "backupPath": "[maintainer-local-ghidra-backup-root]\\BEA_20260519-140648_post_wave593_debug_volume_overlay_verified",
        "fileCount": 19,
        "totalBytes": 160992135.0,
        "missingCount": 0,
        "extraCount": 0,
        "diffCount": 0,
        "manifestHash": "7dee8981c3fdc433ca3d28f7e02c8d1895a6c7a2c616a1355c9dc8f6597b66b9",
    }
    for key, expected_value in expected_backup.items():
        actual = backup.get(key)
        if actual != expected_value:
            failures.append(f"backup {key} mismatch: {actual} != {expected_value}")


def check_docs(failures: list[str]) -> None:
    docs = {
        "public note": read_text(PUBLIC_NOTE),
        "function index": read_text(FUNCTION_INDEX),
        "thing doc": read_text(THING_DOC),
        "mesh renderer doc": read_text(MESH_RENDERER_DOC),
        "engine doc": read_text(ENGINE_DOC),
        "ghidra reference": read_text(GHIDRA_REFERENCE),
        "campaign": read_text(CAMPAIGN),
        "backlog": read_text(BACKLOG),
        "ledger": read_text(LEDGER),
        "attempt log": read_text(ATTEMPT_LOG),
    }
    required_tokens = (
        "Wave593",
        TARGET,
        TARGET_NAME,
        "CVBufTexture__SetStateCacheModeByFlag",
        "3033",
        "3060",
        "1347",
        "1100",
        "2987/6093 = 49.02%",
        "[maintainer-local-ghidra-backup-root]\\BEA_20260519-140648_post_wave593_debug_volume_overlay_verified",
    )
    for label, text in docs.items():
        require_tokens(label, text, required_tokens[:3], failures)
    for label in ("public note", "function index", "ghidra reference", "campaign", "backlog", "ledger", "attempt log"):
        require_tokens(label, docs[label], required_tokens, failures)
    for label, text in docs.items():
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{label} overclaims: {token}")


def run_checks() -> list[str]:
    failures: list[str] = []
    checks = (
        check_logs,
        check_post_exports,
        check_xrefs,
        check_instruction_evidence,
        check_queue_and_backup,
        check_docs,
    )
    for check in checks:
        try:
            check(failures)
        except Exception as exc:  # noqa: BLE001 - report all probe failures together.
            failures.append(f"{check.__name__} raised {type(exc).__name__}: {exc}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Exit non-zero on validation failure")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    failures = run_checks()
    payload = {"status": "PASS" if not failures else "FAIL", "failures": failures}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"ghidra_debug_volume_overlay_wave593_probe: {payload['status']}")
        for failure in failures:
            print(f"- {failure}")
    return 1 if args.check and failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
