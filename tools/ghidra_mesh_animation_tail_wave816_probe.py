#!/usr/bin/env python3
"""Validate Wave816 mesh-animation-tail read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave816-mesh-animation-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_mesh_animation_tail_wave816_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
MESH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "mesh.cpp" / "_index.md"
MESHPART_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MeshPart.cpp" / "_index.md"
MECH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Mech.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260524-151844_post_wave816_mesh_animation_tail_verified"

TARGET_SIGNATURES = {
    "0x004b0cd0": "void * __thiscall CMesh__SelectModeSpecificPtr(void * this)",
    "0x004b0d00": "void __thiscall CMeshPart__InterpolateSegmentTransform(void * this, int frame_a, int frame_b, float frame_lerp, void * out_transform_3x4, float * out_anchor_vec4)",
    "0x004b0fb0": "void __thiscall CMCMech__BuildInterpolatedPoseAndAnchor(void * this, int frame_a, int frame_b, int blend_step_or_flag, void * optional_pose_controller, void * out_transform_3x4, float * out_anchor_vec4, int cache_slot, int notify_callbacks, int force_recursive_path)",
}

TARGET_NAMES = {
    "0x004b0cd0": "CMesh__SelectModeSpecificPtr",
    "0x004b0d00": "CMeshPart__InterpolateSegmentTransform",
    "0x004b0fb0": "CMCMech__BuildInterpolatedPoseAndAnchor",
}

COMMENT_TOKENS = {
    "0x004b0cd0": ("Wave816 static read-back", "+0x8c", "+0x124", "15 call xrefs"),
    "0x004b0d00": ("Wave816 static read-back/signature hardening", "0x004b17fc", "RET 0x14", "+0xb8", "+0xc4", "+0xc8", "+0x10c"),
    "0x004b0fb0": ("Wave816 static read-back/signature hardening", "RET 0x24", "DAT_00704cf0", "DAT_00704d20", "+0x98", "+0x104", "+0x108", "+0x70"),
}

COMMON_TAGS = {
    "static-reaudit",
    "mesh-animation-tail-wave816",
    "wave816-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
}

CORE_ANCHORS = (
    "Wave816 mesh animation tail",
    "mesh-animation-tail-wave816",
    "0x004b0cd0 CMesh__SelectModeSpecificPtr",
    "0x004b0d00 CMeshPart__InterpolateSegmentTransform",
    "0x004b0fb0 CMCMech__BuildInterpolatedPoseAndAnchor",
    "RET 0x14",
    "RET 0x24",
    "5602/6098 = 91.87%",
    "0x004b4ba0 CMeshPart__PopulatePoseCacheRecursive",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime animation behavior proven",
    "runtime render behavior proven",
    "runtime collision behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
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


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict_clean


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 3,
        "pre-tags.tsv": 3,
        "pre-xrefs.tsv": 56,
        "pre-instructions.tsv": 387,
        "pre-decompile/index.tsv": 3,
        "pre-callsite-instructions.tsv": 525,
        "post-metadata.tsv": 3,
        "post-tags.tsv": 3,
        "post-xrefs.tsv": 56,
        "post-instructions.tsv": 567,
        "post-decompile/index.tsv": 3,
        "post-callsite-instructions.tsv": 525,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, signature in TARGET_SIGNATURES.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row:
            require(row.get("name") == TARGET_NAMES[address], f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in COMMENT_TOKENS[address]:
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=3 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=3 skipped=0 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=3 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=3 found=3 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=3 missing=0",
        "post-xrefs.log": "Wrote 56 rows",
        "post-instructions.log": "Wrote 567 instruction rows",
        "post-decompile.log": "targets=3 dumped=3 missing=0 failed=0",
        "post-callsite-instructions.log": "Wrote 525 instruction rows",
        "quality-refresh.log": "total_functions=6098 commented_functions=5602",
        "queue-probe.log": "Commentless functions: 496",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave816.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave816_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 496, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5602, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5602, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x004b4ba0", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CMeshPart__PopulatePoseCacheRecursive", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171346823, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        MESH_DOC,
        MESHPART_DOC,
        MECH_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-mesh-animation-tail-wave816") == r"py -3 tools\ghidra_mesh_animation_tail_wave816_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave816 mesh animation tail" for row in ledger_rows), "missing Wave816 ledger row", failures)
    require(
        any(row.get("task") == "Wave816 mesh animation tail" and row.get("attempt_id") == 20471 for row in attempts),
        "missing Wave816 attempt row",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave816 mesh-animation-tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave816 mesh-animation-tail probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
