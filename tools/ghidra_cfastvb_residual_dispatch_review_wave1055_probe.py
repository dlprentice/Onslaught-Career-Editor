#!/usr/bin/env python3
"""Validate Wave1055 CFastVB residual dispatch review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1055-cfastvb-residual-dispatch-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cfastvb_residual_dispatch_review_wave1055_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1055_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FASTVB_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260601-173102_post_wave1055_cfastvb_residual_dispatch_review_verified"

TARGETS = {
    "0x0059f360": "CFastVB__DispatchOp_TransformVec4_0059f360",
    "0x0059f3d9": "CFastVB__DispatchOp_NormalizeVec4_0059f3d9",
    "0x0059f473": "CFastVB__DispatchOp_NormalizeVec4Scaled_0059f473",
    "0x0059f4f1": "CFastVB__DispatchOp_EulerToQuaternion_0059f4f1",
    "0x0059f5b3": "CFastVB__BuildOrthonormalBasisFromCovariance",
    "0x005a14a5": "CFastVB__DispatchOp_BuildPlaneFromTriangle_005a14a5",
    "0x005a15a5": "CFastVB__DispatchOp_QuaternionToMatrix4_005a15a5",
    "0x005a16b1": "CFastVB__DispatchOp_TransformVec3ByMatrix4_005a16b1",
    "0x005a1786": "CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a1786",
    "0x005a1889": "CFastVB__DispatchOp_NormalizeVec3_005a1889",
    "0x005a1979": "CFastVB__DispatchOp_NormalizeVec4_005a1979",
    "0x005a1c55": "CFastVB__DispatchOp_TransformVec4Batch_Alt_005a1c55",
    "0x005a1e5b": "CFastVB__DispatchOp_TransformVec4BatchW_Alt_005a1e5b",
    "0x005a1fe9": "CFastVB__DispatchOp_TransformProjectVec4Batch_Alt_005a1fe9",
    "0x005a214f": "CFastVB__DispatchOp_TransformVec4Batch_NoOffset_Alt_005a214f",
    "0x005a225f": "CFastVB__DispatchOp_TransformVec4Batch_Perspective_Alt_005a225f",
    "0x005a249d": "CFastVB__DispatchOp_TransformVec3WBatch_Alt_005a249d",
    "0x005a2a61": "CFastVB__DispatchOp_TransformVec2ByMatrix4",
    "0x005a2ee9": "CFastVB__DispatchOp_Determinant4x4_005a2ee9",
    "0x005a2ff4": "CFastVB__DispatchOp_BuildPlaneFromTriangle_Alt_005a2ff4",
    "0x005a30f4": "CFastVB__DispatchOp_QuaternionToMatrix4_Alt_005a30f4",
    "0x005a3200": "CFastVB__DispatchOp_TransformVec4ByMatrix4_005a3200",
    "0x005a32d4": "CFastVB__DispatchOp_MultiplyMatrix4x4_005a32d4",
    "0x005a3508": "CFastVB__DispatchOp_BuildMatrix4FromQuaternionPair_005a3508",
    "0x005a36cf": "CFastVB__DispatchOp_BuildQuaternionFromEulerAngles_005a36cf",
    "0x005a3791": "CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_005a3791",
}

CONTEXT_NAMES = {
    "0x005980be": "CFastVB__InitDispatchTableVariant_005980be",
    "0x0059822c": "CFastVB__InitDispatchTableVariant_0059822c",
    "0x00598474": "CFastVB__InitDispatchOpsFromFeatureFlags",
    "0x0059f6dd": "CFastVB__BroadcastMatrix4x4ToSIMDLanes",
    "0x005a04a0": "CFastVB__DispatchOp_WeightedMatrixBlendBatch_005a04a0",
    "0x005a0f50": "CFastVB__EvaluateCubicBasisVec3",
    "0x005a38c0": "CFastVB__DispatchOp_TransformVec4ArrayByMatrix4",
    "0x005a4d98": "CFastVB__DispatchOp_InterpolateQuaternionPairCore_005a4d98",
    "0x005a5052": "CFastVB__DispatchOp_NormalizeQuaternionWithAcosFallback_005a5052",
    "0x005a647f": "CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Core_005a647f",
    "0x005a8f5d": "CFastVB__DispatchOp_InvertMatrix4x4_WithDeterminant_005a8f5d",
    "0x005a9d78": "CFastVB__DispatchOp_MultiplyMatrix4x4_Packed_005a9d78",
}

DOC_TOKENS = (
    "Wave1055",
    "cfastvb-residual-dispatch-review-wave1055",
    "0x0059f360 CFastVB__DispatchOp_TransformVec4_0059f360",
    "0x0059f3d9 CFastVB__DispatchOp_NormalizeVec4_0059f3d9",
    "0x005a16b1 CFastVB__DispatchOp_TransformVec3ByMatrix4_005a16b1",
    "0x005a225f CFastVB__DispatchOp_TransformVec4Batch_Perspective_Alt_005a225f",
    "0x005a2ee9 CFastVB__DispatchOp_Determinant4x4_005a2ee9",
    "0x005a3508 CFastVB__DispatchOp_BuildMatrix4FromQuaternionPair_005a3508",
    "0x005a3791 CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_005a3791",
    "CFastVB__InitDispatchTableVariant_005980be",
    "CFastVB__InitDispatchTableVariant_0059822c",
    "CFastVB__BroadcastMatrix4x4ToSIMDLanes",
    "769/1408 = 54.62%",
    "1091/1509 = 72.30%",
    "500/500 = 100.00%",
    "6246/6246 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime gameplay behavior proven",
    "runtime proof complete",
    "patch behavior proven",
    "rebuild parity proven",
    "all systems complete",
    "every system is complete",
    "fully reverse-engineered",
    "fully reverse engineered",
    "exact source-layout identity proven",
    "exact source layout identity proven",
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


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 26,
        "tags.tsv": 26,
        "xrefs.tsv": 50,
        "instructions.tsv": 2277,
        "decompile/index.tsv": 26,
        "context-metadata.tsv": 12,
        "context-tags.tsv": 12,
        "context-xrefs.tsv": 45,
        "context-instructions.tsv": 2263,
        "context-decompile/index.tsv": 12,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile" / "index.tsv")}
    for address, name in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            require(row.get("comment", "").strip(), f"missing comment at {address}", failures)
            require("Static retail Ghidra" in row.get("comment", ""), f"missing static-boundary wording at {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require({"static-reaudit", "retail-binary-evidence", "comment-hardened"}.issubset(actual_tags), f"missing common tags at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("name") == name, f"decompile name mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    context = {normalize_address(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}
    for address, name in CONTEXT_NAMES.items():
        ctx = context.get(address)
        require(ctx is not None, f"missing context metadata for {address}", failures)
        if ctx is not None:
            require(ctx.get("name") == name, f"context name mismatch at {address}", failures)
            require(ctx.get("status") == "OK", f"context status mismatch at {address}", failures)

    xrefs = read_tsv(BASE / "xrefs.tsv")
    require({normalize_address(row["target_addr"]) for row in xrefs} == set(TARGETS), "xref target set mismatch", failures)
    xref_text = read_text(BASE / "xrefs.tsv") + read_text(BASE / "context-xrefs.tsv")
    for token in (
        "CFastVB__InitDispatchTableVariant_005980be",
        "CFastVB__InitDispatchTableVariant_0059822c",
        "CFastVB__DispatchOp_TransformVec4Batch_Alt_005a1c55",
        "CFastVB__DispatchOp_TransformVec4ByMatrix4_005a3200",
    ):
        require(token in xref_text, f"missing xref evidence token: {token}", failures)

    evidence_text = "\n".join(
        [
            read_text(BASE / "metadata.tsv"),
            read_text(BASE / "tags.tsv"),
            read_text(BASE / "context-metadata.tsv"),
            *[path.read_text(encoding="utf-8-sig") for path in (BASE / "decompile").glob("*.c")],
            *[path.read_text(encoding="utf-8-sig") for path in (BASE / "context-decompile").glob("*.c")],
        ]
    )
    for token in (
        "CFastVB__BroadcastMatrix4x4ToSIMDLanes",
        "stack-locked",
        "runtime math correctness",
        "CFastVB__DispatchOp_MultiplyMatrix4x4_Packed_005a9d78",
    ):
        require(token in evidence_text, f"missing artifact evidence token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "metadata.log": "targets=26 found=26 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=26 missing=0",
        "xrefs.log": "Wrote 50 rows",
        "instructions.log": "Wrote 2277 function-body instruction rows",
        "decompile.log": "targets=26 dumped=26 missing=0 failed=0",
        "context-metadata.log": "targets=12 found=12 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "context-xrefs.log": "Wrote 45 rows",
        "context-instructions.log": "Wrote 2263 function-body instruction rows",
        "context-decompile.log": "targets=12 dumped=12 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "BADNAME", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6246, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    rows = read_tsv(QUEUE_TSV)
    require(len(rows) == 6246, "quality TSV row count mismatch", failures)
    require(all(row.get("comment", "").strip() for row in rows), "quality TSV contains commentless row", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 174656391 or backup.get("totalBytes") == 174656391.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        PUBLIC_NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        FASTVB_INDEX,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-cfastvb-residual-dispatch-review-wave1055")
        == r"py -3 tools\ghidra_cfastvb_residual_dispatch_review_wave1055_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1055-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1055 --check",
        "missing aggregate package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1055 cfastvb residual dispatch review" for row in ledger_rows), "missing Wave1055 ledger row", failures)
    require(
        any(row.get("task") == "Wave1055 cfastvb residual dispatch review" and row.get("attempt_id") == 20637 for row in attempts),
        "missing Wave1055 attempt row",
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
        print("Wave1055 CFastVB residual dispatch review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1055 CFastVB residual dispatch review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
