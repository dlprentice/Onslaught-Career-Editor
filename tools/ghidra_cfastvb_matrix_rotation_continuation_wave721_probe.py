#!/usr/bin/env python3
"""Validate Wave721 CFastVB matrix/rotation continuation read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave721-cfastvb-matrix-rotation-continuation"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cfastvb_matrix_rotation_continuation_wave721_2026-05-22.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

COMMON_TAGS = {
    "static-reaudit",
    "cfastvb-matrix-rotation-continuation-wave721",
    "wave721-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "cfastvb-matrix-rotation-continuation",
}

TARGETS = {
    "0x005a62bf": (
        "CFastVB__DispatchOp_InitIdentityMatrix4x4_005a62bf",
        "void __cdecl CFastVB__DispatchOp_InitIdentityMatrix4x4_005a62bf(float * out_matrix4x4)",
        ("identity matrix4x4 initializer", "sixteen-float matrix", "FastExitMediaState"),
        COMMON_TAGS | {"signature-hardened", "matrix4x4", "identity", "composition-helper", "tranche-head"},
    ),
    "0x005a647f": (
        "CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Core_005a647f",
        "int CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Core_005a647f(void)",
        ("optional-transform composition core", "Signature intentionally left unchanged", "locked parameter storage"),
        COMMON_TAGS | {"comment-only", "hidden-stack-context", "matrix4x4", "optional-inputs", "composition", "stack-locked", "simd-helper"},
    ),
    "0x005a7617": (
        "CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles",
        "void __stdcall CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles(void * param_1, int param_2, int param_3)",
        ("Euler-angle-to-matrix4 dispatch", "0x005ef190", "exact packed argument ABI remains unresolved"),
        COMMON_TAGS | {"comment-only", "hidden-stack-context", "matrix4x4", "rotation", "euler-angles", "fast-trig", "packed-stack-abi", "dispatch-table"},
    ),
    "0x005a7cf0": (
        "CFastVB__DispatchOp_BuildRotationMatrixFromAxisAngleVector",
        "void __stdcall CFastVB__DispatchOp_BuildRotationMatrixFromAxisAngleVector(float * out_matrix4x4, float * axis_angle_vec3)",
        ("axis-angle-vector-to-matrix4 dispatch", "CFastVB__DispatchOp_NormalizeVec3_Packed_005a9a5f", "fast trig pair"),
        COMMON_TAGS | {"signature-hardened", "matrix4x4", "rotation", "axis-angle", "normalize", "fast-trig", "dispatch-table"},
    ),
    "0x005a7e09": (
        "CFastVB__DispatchOp_ComposeMatrixFromOptionalTransforms",
        "int CFastVB__DispatchOp_ComposeMatrixFromOptionalTransforms(void)",
        ("optional transform matrix composition dispatch", "Signature intentionally left unchanged", "locked parameter storage"),
        COMMON_TAGS | {"comment-only", "hidden-stack-context", "matrix4x4", "optional-transforms", "composition", "stack-locked", "dispatch-table"},
    ),
    "0x005a8f5d": (
        "CFastVB__DispatchOp_InvertMatrix4x4_WithDeterminant_005a8f5d",
        "void __stdcall CFastVB__DispatchOp_InvertMatrix4x4_WithDeterminant_005a8f5d(float * out_inverse_matrix4x4, float * out_determinant_or_null, float * input_matrix4x4)",
        ("matrix4x4 inverse dispatch", "optional output pointer", "reciprocal-determinant-scaled inverse matrix"),
        COMMON_TAGS | {"signature-hardened", "matrix4x4", "inverse", "determinant", "cofactor", "dispatch-table", "simd-helper"},
    ),
    "0x005a9637": (
        "CFastVB__DispatchOp_InvertMatrix4x4_Variant_005a9637",
        "int __stdcall CFastVB__DispatchOp_InvertMatrix4x4_Variant_005a9637(float * out_inverse_matrix4x4, float * out_determinant_or_null, float * input_matrix4x4)",
        ("scalar matrix4x4 inverse variant", "returns zero when the determinant is zero", "output pointer as an int-compatible value"),
        COMMON_TAGS | {"signature-hardened", "matrix4x4", "inverse", "determinant", "cofactor", "scalar-helper", "pointer-return"},
    ),
    "0x005a99f8": (
        "CFastVB__DispatchOp_TransformVec3ByMatrix4_NoTranslation_005a99f8",
        "int __stdcall CFastVB__DispatchOp_TransformVec3ByMatrix4_NoTranslation_005a99f8(float * out_vec3, float * input_vec3, float * matrix4x4)",
        ("Vec3-by-matrix4 helper", "without adding translation terms", "output pointer as an int-compatible value"),
        COMMON_TAGS | {"signature-hardened", "vec3", "matrix4x4", "transform", "no-translation", "dispatch-table", "pointer-return"},
    ),
    "0x005a9a5f": (
        "CFastVB__DispatchOp_NormalizeVec3_Packed_005a9a5f",
        "void __stdcall CFastVB__DispatchOp_NormalizeVec3_Packed_005a9a5f(float * out_vec3, float * input_vec3)",
        ("packed Vec3 normalization helper", "reciprocal-square-root refinement", "FastExitMediaState"),
        COMMON_TAGS | {"signature-hardened", "vec3", "normalize", "packed", "rsqrt", "dispatch-table", "shared-helper"},
    ),
    "0x005a9ced": (
        "CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a9ced",
        "int __stdcall CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a9ced(float * out_vec3, float * input_vec3, float * matrix4x4)",
        ("Vec3 transform/project helper", "reciprocal from the projected w lane", "output pointer as an int-compatible value"),
        COMMON_TAGS | {"signature-hardened", "vec3", "matrix4x4", "transform", "project", "reciprocal-w", "pointer-return"},
    ),
    "0x005a9d78": (
        "CFastVB__DispatchOp_MultiplyMatrix4x4_Packed_005a9d78",
        "int __stdcall CFastVB__DispatchOp_MultiplyMatrix4x4_Packed_005a9d78(float * out_matrix4x4, float * left_matrix4x4, float * right_matrix4x4)",
        ("packed matrix4x4 multiply helper", "writes sixteen output floats", "output pointer as an int-compatible value"),
        COMMON_TAGS | {"signature-hardened", "matrix4x4", "multiply", "packed", "composition-helper", "pointer-return"},
    ),
    "0x005a9f3f": (
        "CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_Alt_005a9f3f",
        "int __stdcall CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_Alt_005a9f3f(float * out_vec3, float * input_vec3, float * matrix4x4)",
        ("alternate Vec3 transform/project dispatch", "reciprocal-w scaling", "three output floats"),
        COMMON_TAGS | {"signature-hardened", "vec3", "matrix4x4", "transform", "project", "alternate-dispatch", "dispatch-table", "pointer-return", "tranche-tail"},
    ),
}

DOC_TOKENS = (
    "Wave721 CFastVB matrix/rotation continuation",
    "cfastvb-matrix-rotation-continuation-wave721",
    "0x005a62bf CFastVB__DispatchOp_InitIdentityMatrix4x4_005a62bf",
    "0x005a7617 CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles",
    "0x005a7cf0 CFastVB__DispatchOp_BuildRotationMatrixFromAxisAngleVector",
    "0x005a8f5d CFastVB__DispatchOp_InvertMatrix4x4_WithDeterminant_005a8f5d",
    "0x005a9d78 CFastVB__DispatchOp_MultiplyMatrix4x4_Packed_005a9d78",
    "0x005aa480 CFastVB__DispatchOp_ConvertPackedS16ToFloatPairBatch_005aa480",
    "0x0042f220 CSPtrSet__Clear",
    r"[maintainer-local-ghidra-backup-root]\BEA_20260522-043029_post_wave721_cfastvb_matrix_rotation_continuation_verified",
)

OVERCLAIM_TOKENS = (
    "runtime math correctness proven",
    "runtime transform fidelity proven",
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


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 12,
        "pre-tags.tsv": 12,
        "pre-xrefs.tsv": 38,
        "pre-instructions.tsv": 1356,
        "pre-decompile/index.tsv": 12,
        "post-metadata.tsv": 12,
        "post-tags.tsv": 12,
        "post-xrefs.tsv": 38,
        "post-instructions.tsv": 1356,
        "post-instructions-wide.tsv": 3420,
        "post-decompile/index.tsv": 12,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, (name, signature, comment_tokens, expected_tags) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch at {address}", failures)
        require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
        comment = row.get("comment", "")
        require("Wave721 static read-back" in comment, f"missing Wave721 comment at {address}", failures)
        require("Static retail Ghidra metadata" in comment, f"missing static-evidence boundary at {address}", failures)
        for token in comment_tokens:
            require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(expected_tags.issubset(actual_tags), f"tags missing at {address}: {expected_tags - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)
        require((BASE / "post-decompile" / f"{address[2:]}_{name}.c").is_file(), f"missing decompile file for {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=9 comment_only_updated=3 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=12 skipped=0 renamed=0 would_rename=0 signature_updated=8 comment_only_updated=3 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "pre-metadata.log": "targets=12 found=12 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "pre-xrefs.log": "Wrote 38 rows",
        "pre-instructions.log": "Wrote 1356 instruction rows",
        "pre-decompile.log": "targets=12 dumped=12 missing=0 failed=0",
        "post-metadata.log": "targets=12 found=12 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "post-xrefs.log": "Wrote 38 rows",
        "post-instructions.log": "Wrote 1356 instruction rows",
        "post-instructions-wide.log": "Wrote 3420 instruction rows",
        "post-decompile.log": "targets=12 dumped=12 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}", failures)
        require("LockException" not in text, f"unexpected LockException in {relative}", failures)
        require("MISSING:" not in text, f"unexpected MISSING in {relative}", failures)
        require("BAD:" not in text, f"unexpected BAD in {relative}", failures)

    require("REPORT: Save succeeded" in read_text(BASE / "apply.log"), "missing apply save evidence", failures)
    require("REPORT: Save succeeded" in read_text(BASE / "apply-final-dry.log"), "missing final dry save evidence", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 1850, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 1216, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 118, "param count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005aa480", "high-signal head address mismatch", failures)
    require(high_signal["name"] == "CFastVB__DispatchOp_ConvertPackedS16ToFloatPairBatch_005aa480", "high-signal head name mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    raw_head = next(row for row in rows if not row.get("comment", "").strip())
    require(commented == 4248, "commented count mismatch", failures)
    require(strict_clean == 4190, "strict clean-signature proxy mismatch", failures)
    require(raw_head["address"] == "0x0042f220", "raw commentless head address mismatch", failures)
    require(raw_head["name"] == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup["backup"] == r"[maintainer-local-ghidra-backup-root]\BEA_20260522-043029_post_wave721_cfastvb_matrix_rotation_continuation_verified", "backup destination mismatch", failures)
    require(backup["sourceFileCount"] == 19, "backup source file count mismatch", failures)
    require(backup["backupFileCount"] == 19, "backup file count mismatch", failures)
    require(int(backup["backupBytes"]) == 166464391, "backup byte count mismatch", failures)
    require(backup["diffCount"] == 0, "backup diff count mismatch", failures)


def check_docs_and_state(failures: list[str]) -> None:
    docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        FASTVB_DOC,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            escaped = token.replace("\\", "\\\\")
            require(token in text or escaped in text, f"missing doc token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lower, f"overclaim token in {path.relative_to(ROOT)}: {token}", failures)

    require("test:ghidra-cfastvb-matrix-rotation-continuation-wave721" in read_text(PACKAGE_JSON), "missing package script", failures)

    ledgers = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave721 CFastVB matrix/rotation continuation" for row in ledgers), "missing Wave721 ledger row", failures)
    require(any(row.get("attempt_id") == 20376 and row.get("task") == "Wave721 CFastVB matrix/rotation continuation" for row in attempts), "missing Wave721 attempt row", failures)

    tracking = read_json(TRACKING)
    require(tracking["next_attempt_id"] == 20377, "tracking next_attempt_id mismatch", failures)
    require("Wave721 CFastVB matrix/rotation continuation" in tracking.get("current_focus", ""), "tracking focus mismatch", failures)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs_and_state(failures)

    if failures:
        print("Wave721 CFastVB matrix/rotation continuation probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave721 CFastVB matrix/rotation continuation probe: PASS")
    print(f"Targets: {len(TARGETS)}")
    print("Queue: 6098 total, 4248 commented, 1850 commentless, 1216 undefined, 118 param_N")
    print(r"Backup: [maintainer-local-ghidra-backup-root]\BEA_20260522-043029_post_wave721_cfastvb_matrix_rotation_continuation_verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
