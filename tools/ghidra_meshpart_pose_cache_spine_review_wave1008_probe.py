#!/usr/bin/env python3
"""Validate Wave1008 MeshPart pose-cache spine review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1008-meshpart-pose-cache-spine-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_meshpart_pose_cache_spine_review_wave1008_2026-05-31.md"
RECHECK_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1008_recheck_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
MESHPART_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MeshPart.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260531-150639_post_wave1008_meshpart_pose_cache_spine_review_verified"

TARGETS = {
    "0x004b4ba0": (
        "CMeshPart__PopulatePoseCacheRecursive",
        "int __thiscall CMeshPart__PopulatePoseCacheRecursive(void * this, float anchor_x, float anchor_y, float anchor_z, float anchor_w, int transform_dword00, int transform_dword01, int transform_dword02, int transform_dword03, int transform_dword04, int transform_dword05, int transform_dword06, int transform_dword07, int transform_dword08, int transform_dword09, int transform_dword10, int transform_dword11, void * mesh_part, int frame_arg0, int frame_arg1, int cache_value)",
        ("Wave817 static read-back", "RET 0x50", "CMeshPart__EvaluateAnimatedTransformCore", "0x004b4ca1", "0x004b4dbc"),
    ),
    "0x004b4cd0": (
        "CMeshPart__RefreshCachedPoseIfStale",
        "int __thiscall CMeshPart__RefreshCachedPoseIfStale(void * this, void * mesh_context, void * pose_controller, int unused_stack_arg2, int force_refresh)",
        ("DAT_008a9aac", "RET 0x10", "DAT_00704db8", "mesh_context+0x160", "CMeshPart__PopulatePoseCacheRecursive"),
    ),
    "0x004b4de0": (
        "CMeshPart__EvaluatePoseTransformForFrame",
        "int __cdecl CMeshPart__EvaluatePoseTransformForFrame(void * animation_context, void * pose_controller, void * mesh_part, float * out_anchor_vec4, float * out_transform_3x4, int skip_controller_transform, int unused_stack_arg6)",
        ("DAT_00704de8", "DAT_00704db8", "ADD ESP, 0x1c", "CMeshPart__RefreshCachedPoseIfStale", "Vec3__SetXYZ", "Mat34__SetRows"),
    ),
}

CONTEXT_TARGETS = {
    "0x004b0d00": "CMeshPart__InterpolateSegmentTransform",
    "0x004b0fb0": "CMCMech__BuildInterpolatedPoseAndAnchor",
    "0x004b24d0": "CMeshPart__ResolveWrappedFrameIndexAndLerp",
    "0x004b5330": "CMeshPart__EvaluateAnimatedTransformCore",
    "0x00401ec0": "Vec3__SetXYZ",
    "0x00401f10": "Mat34__SetRows",
}

EXPECTED_XREFS = {
    "0x004b4ba0": {"0x004b4dbc", "0x004b4ca1"},
    "0x004b4cd0": {"0x004b6296", "0x004b4e81"},
    "0x004b4de0": {"0x00445130", "0x004ad70a", "0x004dd1cf", "0x004dede9"},
}

DOC_TOKENS = (
    "Wave1008",
    "meshpart-pose-cache-spine-review-wave1008",
    "0x004b4ba0 CMeshPart__PopulatePoseCacheRecursive",
    "0x004b4cd0 CMeshPart__RefreshCachedPoseIfStale",
    "0x004b4de0 CMeshPart__EvaluatePoseTransformForFrame",
    "0x004b0d00 CMeshPart__InterpolateSegmentTransform",
    "0x004b0fb0 CMCMech__BuildInterpolatedPoseAndAnchor",
    "0x004b24d0 CMeshPart__ResolveWrappedFrameIndexAndLerp",
    "0x004b5330 CMeshPart__EvaluateAnimatedTransformCore",
    "499/1408 = 35.44%",
    "679/1478 = 45.94%",
    "398/500 = 79.60%",
    "6223/6223 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime animation behavior proven",
    "runtime collision behavior proven",
    "runtime render behavior proven",
    "exact aggregate c types proven",
    "exact source-body identity proven",
    "exact layout proven",
    "rebuild parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig", errors="replace").replace("\x00", "")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value in {"", "<none>"}:
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def row_by_address(rows: list[dict[str, str]], address: str, field: str = "address") -> dict[str, str] | None:
    target = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(field, "")) == target:
            return row
    return None


def contains_token(text: str, token: str) -> bool:
    return (
        token in text
        or token.replace("\\", "\\\\") in text
        or token.replace("\\", "\\\\\\\\") in text
        or token.replace("\\\\", "\\") in text.replace("\\\\\\\\", "\\").replace("\\\\", "\\")
    )


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 3,
        "pre-tags.tsv": 3,
        "pre-xrefs.tsv": 8,
        "pre-instructions.tsv": 467,
        "pre-decompile/index.tsv": 3,
        "context-metadata.tsv": 6,
        "context-xrefs.tsv": 708,
        "context-instructions.tsv": 1622,
        "context-decompile/index.tsv": 6,
        "callsite-instructions.tsv": 105,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = read_tsv(BASE / "pre-metadata.tsv")
    tags = read_tsv(BASE / "pre-tags.tsv")
    decompile_index = read_tsv(BASE / "pre-decompile" / "index.tsv")
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")
    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = row_by_address(metadata, address)
        require(row is not None, f"metadata missing {address}", failures)
        if row:
            require(row.get("name") == name, f"metadata name mismatch {address}", failures)
            require(row.get("signature") == signature, f"metadata signature mismatch {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            comment = row.get("comment", "")
            for token in comment_tokens:
                require(token in comment, f"comment token missing {address}: {token}", failures)

        dec = row_by_address(decompile_index, address)
        require(dec is not None, f"decompile missing {address}", failures)
        if dec:
            require(dec.get("name") == name, f"decompile name mismatch {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

        tag_row = row_by_address(tags, address)
        require(tag_row is not None, f"tags missing {address}", failures)
        if tag_row:
            actual_tags = set(filter(None, tag_row.get("tags", "").split(";")))
            for tag in ("static-reaudit", "retail-binary-evidence", "comment-hardened", "meshpart-pose-cache-wave817", "wave817-readback-verified"):
                require(tag in actual_tags, f"missing tag {address}: {tag}", failures)

        actual_froms = {
            normalize_address(row.get("from_addr", ""))
            for row in xrefs
            if normalize_address(row.get("target_addr", "")) == address
        }
        require(EXPECTED_XREFS[address].issubset(actual_froms), f"xrefs missing for {address}: {EXPECTED_XREFS[address] - actual_froms}", failures)

    context = read_tsv(BASE / "context-metadata.tsv")
    context_index = read_tsv(BASE / "context-decompile" / "index.tsv")
    for address, name in CONTEXT_TARGETS.items():
        row = row_by_address(context, address)
        require(row is not None, f"context metadata missing {address}", failures)
        if row:
            require(row.get("name") == name, f"context name mismatch {address}", failures)
            require(row.get("status") == "OK", f"context status mismatch {address}", failures)
        dec = row_by_address(context_index, address)
        require(dec is not None, f"context decompile missing {address}", failures)
        if dec:
            require(dec.get("name") == name, f"context decompile name mismatch {address}", failures)
            require(dec.get("status") == "OK", f"context decompile status mismatch {address}", failures)

    refresh_text = read_text(BASE / "pre-decompile" / "004b4cd0_CMeshPart__RefreshCachedPoseIfStale.c")
    for token in ("DAT_008a9aac", "DAT_00704db8", "CMeshPart__PopulatePoseCacheRecursive"):
        require(token in refresh_text, f"refresh decompile missing {token}", failures)

    eval_text = read_text(BASE / "pre-decompile" / "004b4de0_CMeshPart__EvaluatePoseTransformForFrame.c")
    for token in (
        "DAT_00704de8",
        "DAT_00704db8",
        "CMeshPart__ResolveWrappedFrameIndexAndLerp",
        "CMCMech__BuildInterpolatedPoseAndAnchor",
        "CMeshPart__RefreshCachedPoseIfStale",
        "Vec3__SetXYZ",
        "Mat34__SetRows",
    ):
        require(token in eval_text, f"evaluate decompile missing {token}", failures)

    context_text = read_text(BASE / "context-decompile" / "004b0fb0_CMCMech__BuildInterpolatedPoseAndAnchor.c")
    for token in ("CMeshPart__InterpolateSegmentTransform", "DAT_00704cf0", "DAT_00704d20"):
        require(token in context_text, f"CMCMech context decompile missing {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected_log_tokens = {
        "pre-metadata.log": "targets=3 found=3 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=3 missing=0",
        "pre-xrefs.log": "Wrote 8 rows",
        "pre-instructions.log": "Wrote 467 function-body instruction rows",
        "pre-decompile.log": "targets=3 dumped=3 missing=0 failed=0",
        "context-metadata.log": "targets=6 found=6 missing=0",
        "context-xrefs.log": "Wrote 708 rows",
        "context-instructions.log": "Wrote 1622 function-body instruction rows",
        "context-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "callsite-instructions.log": "Wrote 105 instruction rows",
    }
    for relative, token in expected_log_tokens.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token {relative}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"missing save token in {relative}", failures)
        for bad in ("LockException", "BADADDR", "MISSING:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173869959 or backup.get("totalBytes") == 173869959.0, "backup byte count mismatch", failures)
    for key in ("missingCount", "extraCount", "diffCount", "hashDiffCount"):
        require(backup.get(key) == 0, f"backup {key} mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = (
        NOTE,
        RECHECK_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        MESHPART_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    )
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-meshpart-pose-cache-spine-review-wave1008")
        == r"py -3 tools\ghidra_meshpart_pose_cache_spine_review_wave1008_probe.py --check",
        "missing Wave1008 package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1008-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1008 --check",
        "missing Wave1008 aggregate recheck script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1008 MeshPart pose-cache spine review" for row in ledger_rows), "missing Wave1008 ledger row", failures)
    require(
        any(row.get("task") == "Wave1008 MeshPart pose-cache spine review" and row.get("attempt_id") == 20590 for row in attempts),
        "missing Wave1008 attempt row",
        failures,
    )

    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6223, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "queue param_N mismatch", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs(failures)
    if failures:
        print("Wave1008 MeshPart pose-cache spine review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1008 MeshPart pose-cache spine review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
