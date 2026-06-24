#!/usr/bin/env python3
"""Validate Wave719 CFastVB matrix/quaternion core read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave719-cfastvb-matrix-quaternion-core"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cfastvb_matrix_quaternion_core_wave719_2026-05-22.md"
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
    "cfastvb-matrix-quaternion-core-wave719",
    "wave719-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "cfastvb-matrix-quaternion-core",
}

TARGETS = {
    "0x005a298f": (
        "CFastVB__ConvertHalfToFloatArray_SIMD",
        "int __stdcall CFastVB__ConvertHalfToFloatArray_SIMD(float * out_float32, ushort * in_float16, uint element_count)",
        ("SIMD half-float conversion", "CFastVB__ConvertHalfToFloat8_CheckSpecialCasesSIMD", "int-compatible value"),
        COMMON_TAGS | {"half-float", "float32", "simd", "conversion", "dispatch-table", "tranche-head"},
    ),
    "0x005a2a61": (
        "CFastVB__DispatchOp_TransformVec2ByMatrix4",
        "void __stdcall CFastVB__DispatchOp_TransformVec2ByMatrix4(float * out_vec4, float * input_vec4, float * matrix4x4)",
        ("scalar transform dispatch", "perspective batch tails", "writes four transformed output floats"),
        COMMON_TAGS | {"vec2", "vec4-output", "matrix4x4", "transform", "tail-scalar-dispatch", "dispatch-table"},
    ),
    "0x005a2b2d": (
        "CFastVB__InvertMatrix4x4_WithDeterminant",
        "float * __stdcall CFastVB__InvertMatrix4x4_WithDeterminant(float * out_inverse_matrix4x4, float * out_determinant_or_null, float * input_matrix4x4)",
        ("matrix4x4 inverse", "optional output pointer", "reciprocal-determinant-scaled inverse"),
        COMMON_TAGS | {"matrix4x4", "inverse", "determinant", "cofactor", "dispatch-table"},
    ),
    "0x005a2e29": (
        "CFastVB__ComputeAdjugateVec4_PackedB",
        "void __stdcall CFastVB__ComputeAdjugateVec4_PackedB(float * out_vec4, float * row_a_vec4, float * row_b_vec4, float * row_c_vec4)",
        ("packed adjugate/cofactor", "0x0065e7a0", "four float-bit output lanes"),
        COMMON_TAGS | {"adjugate", "cofactor", "vec4", "matrix", "dispatch-table"},
    ),
    "0x005a2ee9": (
        "CFastVB__DispatchOp_Determinant4x4_005a2ee9",
        "double __stdcall CFastVB__DispatchOp_Determinant4x4_005a2ee9(float * matrix4x4)",
        ("determinant dispatch", "x87-style return model", "double"),
        COMMON_TAGS | {"matrix4x4", "determinant", "dispatch-table", "x87-return-model"},
    ),
    "0x005a2ff4": (
        "CFastVB__DispatchOp_BuildPlaneFromTriangle_Alt_005a2ff4",
        "void __stdcall CFastVB__DispatchOp_BuildPlaneFromTriangle_Alt_005a2ff4(float * out_plane_vec4, float * point_a_vec3, float * point_b_vec3, float * point_c_vec3)",
        ("alternate plane-from-triangle", "cross-product normal", "sign-masked distance"),
        COMMON_TAGS | {"plane", "triangle", "cross-product", "normalize", "dispatch-table"},
    ),
    "0x005a30f4": (
        "CFastVB__DispatchOp_QuaternionToMatrix4_Alt_005a30f4",
        "void __stdcall CFastVB__DispatchOp_QuaternionToMatrix4_Alt_005a30f4(float * out_matrix4x4, float * quaternion_xyzw)",
        ("alternate quaternion-to-matrix4", "0x0065e7e0", "sixteen matrix floats"),
        COMMON_TAGS | {"quaternion", "matrix4x4", "normalize", "dispatch-table"},
    ),
    "0x005a3200": (
        "CFastVB__DispatchOp_TransformVec4ByMatrix4_005a3200",
        "void __stdcall CFastVB__DispatchOp_TransformVec4ByMatrix4_005a3200(float * out_vec4, float * input_vec4, float * matrix4x4)",
        ("scalar Vec4-by-matrix", "Vec4 batch tails", "writes four output floats"),
        COMMON_TAGS | {"vec4", "matrix4x4", "transform", "tail-scalar-dispatch", "dispatch-table"},
    ),
    "0x005a32d4": (
        "CFastVB__DispatchOp_MultiplyMatrix4x4_005a32d4",
        "void __stdcall CFastVB__DispatchOp_MultiplyMatrix4x4_005a32d4(float * out_matrix4x4, float * left_matrix4x4, float * right_matrix4x4)",
        ("matrix4x4 multiply", "left and right 4x4 matrices", "sixteen output floats"),
        COMMON_TAGS | {"matrix4x4", "multiply", "dispatch-table"},
    ),
    "0x005a3508": (
        "CFastVB__DispatchOp_BuildMatrix4FromQuaternionPair_005a3508",
        "void __stdcall CFastVB__DispatchOp_BuildMatrix4FromQuaternionPair_005a3508(float * out_matrix4x4, float * basis_quaternion_xyzw, float * rotation_quaternion_xyzw)",
        ("quaternion-pair-to-matrix", "basis quaternion-like input", "4x4 matrix output"),
        COMMON_TAGS | {"quaternion", "matrix4x4", "basis-transform", "normalize", "dispatch-table"},
    ),
    "0x005a36cf": (
        "CFastVB__DispatchOp_BuildQuaternionFromEulerAngles_005a36cf",
        "void __stdcall CFastVB__DispatchOp_BuildQuaternionFromEulerAngles_005a36cf(float * out_quaternion_xyzw, float angle_x_radians, float angle_y_radians, float angle_z_radians)",
        ("Euler-angle-to-quaternion", "CFastVB__SinCosVec4Approx", "four quaternion floats"),
        COMMON_TAGS | {"quaternion", "euler-angles", "sincos", "dispatch-table"},
    ),
    "0x005a3791": (
        "CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_005a3791",
        "void __stdcall CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_005a3791(float * out_quaternion_xyzw, float * matrix3x3)",
        ("matrix3x3-to-quaternion", "0x005f4340", "largest-diagonal fallback"),
        COMMON_TAGS | {"quaternion", "matrix3x3", "trace", "dispatch-table", "tranche-tail"},
    ),
}

DOC_TOKENS = (
    "Wave719 CFastVB matrix/quaternion core",
    "cfastvb-matrix-quaternion-core-wave719",
    "0x005a298f CFastVB__ConvertHalfToFloatArray_SIMD",
    "0x005a2b2d CFastVB__InvertMatrix4x4_WithDeterminant",
    "0x005a3791 CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_005a3791",
    "0x005a47f2 CFastVB__DispatchOp_ExtractAxisAndOptionalAngle",
    "0x0042f220 CSPtrSet__Clear",
    r"G:\GhidraBackups\BEA_20260522-032725_post_wave719_cfastvb_matrix_quaternion_core_verified",
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
        "pre-xrefs.tsv": 25,
        "pre-instructions.tsv": 1116,
        "pre-instructions-wide.tsv": 3180,
        "pre-decompile/index.tsv": 12,
        "post-metadata.tsv": 12,
        "post-tags.tsv": 12,
        "post-xrefs.tsv": 25,
        "post-instructions.tsv": 1116,
        "post-instructions-wide.tsv": 3180,
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
        require("Wave719 static read-back" in comment, f"missing Wave719 comment at {address}", failures)
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
        "apply-dry.log": "SUMMARY: updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=12 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=12 skipped=0 renamed=0 would_rename=0 signature_updated=12 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "pre-metadata.log": "targets=12 found=12 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "pre-xrefs.log": "Wrote 25 rows",
        "pre-instructions.log": "Wrote 1116 instruction rows",
        "pre-instructions-wide.log": "Wrote 3180 instruction rows",
        "pre-decompile.log": "targets=12 dumped=12 missing=0 failed=0",
        "post-metadata.log": "targets=12 found=12 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "post-xrefs.log": "Wrote 25 rows",
        "post-instructions.log": "Wrote 1116 instruction rows",
        "post-instructions-wide.log": "Wrote 3180 instruction rows",
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
    require(quality["commentlessFunctionCount"] == 1872, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 1216, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 131, "param count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005a47f2", "high-signal head address mismatch", failures)
    require(high_signal["name"] == "CFastVB__DispatchOp_ExtractAxisAndOptionalAngle", "high-signal head name mismatch", failures)

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
    require(commented == 4226, "commented count mismatch", failures)
    require(strict_clean == 4169, "strict clean-signature proxy mismatch", failures)
    require(raw_head["address"] == "0x0042f220", "raw commentless head address mismatch", failures)
    require(raw_head["name"] == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup["destination"] == r"G:\GhidraBackups\BEA_20260522-032725_post_wave719_cfastvb_matrix_quaternion_core_verified", "backup destination mismatch", failures)
    require(backup["fileCount"] == 19, "backup file count mismatch", failures)
    require(int(backup["totalBytes"]) == 166366087, "backup byte count mismatch", failures)
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

    require("test:ghidra-cfastvb-matrix-quaternion-core-wave719" in read_text(PACKAGE_JSON), "missing package script", failures)

    ledgers = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave719 CFastVB matrix/quaternion core" for row in ledgers), "missing Wave719 ledger row", failures)
    require(any(row.get("task") == "Wave719 CFastVB matrix/quaternion core" for row in attempts), "missing Wave719 attempt row", failures)

    tracking = read_json(TRACKING)
    require(tracking["next_attempt_id"] == 20375, "tracking next_attempt_id mismatch", failures)
    require("Wave719 CFastVB matrix/quaternion core" in tracking.get("current_focus", ""), "tracking focus mismatch", failures)


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
        print("Wave719 CFastVB matrix/quaternion core probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave719 CFastVB matrix/quaternion core probe: PASS")
    print(f"Targets: {len(TARGETS)}")
    print("Queue: 6098 total, 4226 commented, 1872 commentless, 1216 undefined, 131 param_N")
    print(r"Backup: G:\GhidraBackups\BEA_20260522-032725_post_wave719_cfastvb_matrix_quaternion_core_verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
