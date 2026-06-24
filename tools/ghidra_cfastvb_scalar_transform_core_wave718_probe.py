#!/usr/bin/env python3
"""Validate Wave718 CFastVB scalar transform core read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave718-cfastvb-scalar-transform-core"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cfastvb_scalar_transform_core_wave718_2026-05-22.md"
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

COMMON_SIGNATURE_TAGS = {
    "static-reaudit",
    "cfastvb-scalar-transform-core-wave718",
    "wave718-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "cfastvb-scalar-transform-core",
}

COMMON_COMMENT_TAGS = {
    "static-reaudit",
    "cfastvb-scalar-transform-core-wave718",
    "wave718-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "comment-only",
    "hidden-stack-context",
    "cfastvb-scalar-transform-core",
}

TARGETS = {
    "0x005a0b22": (
        "CFastVB__ConvertHalfToFloatArray_SSE",
        "int __stdcall CFastVB__ConvertHalfToFloatArray_SSE(float * out_float32, ushort * in_float16, uint element_count)",
        ("half-float conversion", "ConvertHalfToFloat8_SIMDKernel", "integer return type"),
        COMMON_SIGNATURE_TAGS | {"half-float", "float32", "sse", "conversion", "dispatch-table", "tranche-head"},
    ),
    "0x005a0df6": (
        "CFastVB__ComputeAdjugateVec4_PackedA",
        "void __stdcall CFastVB__ComputeAdjugateVec4_PackedA(float * out_vec4, float * row_a_vec4, float * row_b_vec4, float * row_c_vec4)",
        ("adjugate/cofactor", "0x0065e600", "RET 0x10"),
        COMMON_SIGNATURE_TAGS | {"adjugate", "cofactor", "vec4", "matrix", "dispatch-table"},
    ),
    "0x005a0eb6": (
        "CFastVB__NormalizeVec4_ReciprocalSqrt",
        "float * __stdcall CFastVB__NormalizeVec4_ReciprocalSqrt(float * out_vec4, float * input_vec4)",
        ("vec4 normalization", "rsqrtss", "RET 0x8"),
        COMMON_SIGNATURE_TAGS | {"vec4", "normalize", "reciprocal-sqrt", "sse", "dispatch-table"},
    ),
    "0x005a0f50": (
        "CFastVB__EvaluateCubicBasisVec3",
        "int CFastVB__EvaluateCubicBasisVec3(void)",
        ("cubic basis Vec3", "Signature intentionally left unchanged", "locked parameter storage"),
        COMMON_COMMENT_TAGS | {"cubic-basis", "vec3", "stack-locked", "dispatch-table"},
    ),
    "0x005a1002": (
        "CFastVB__EvaluateCubicBasisVec2",
        "int CFastVB__EvaluateCubicBasisVec2(void)",
        ("cubic basis Vec2", "Signature intentionally left unchanged", "locked parameter storage"),
        COMMON_COMMENT_TAGS | {"cubic-basis", "vec2", "stack-locked", "dispatch-table"},
    ),
    "0x005a1087": (
        "CFastVB__EvaluateCubicBasisVec4",
        "int CFastVB__EvaluateCubicBasisVec4(void)",
        ("cubic basis Vec4", "Signature intentionally left unchanged", "locked parameter storage"),
        COMMON_COMMENT_TAGS | {"cubic-basis", "vec4", "stack-locked", "dispatch-table"},
    ),
    "0x005a112c": (
        "CFastVB__DispatchOp_CubicBlendVec3_005a112c",
        "int CFastVB__DispatchOp_CubicBlendVec3_005a112c(void)",
        ("cubic blend Vec3", "Signature intentionally left unchanged", "locked parameter storage"),
        COMMON_COMMENT_TAGS | {"cubic-blend", "vec3", "stack-locked", "dispatch-table"},
    ),
    "0x005a11df": (
        "CFastVB__DispatchOp_CubicBlendVec4_005a11df",
        "int CFastVB__DispatchOp_CubicBlendVec4_005a11df(void)",
        ("cubic blend Vec4", "Signature intentionally left unchanged", "locked parameter storage"),
        COMMON_COMMENT_TAGS | {"cubic-blend", "vec4", "stack-locked", "dispatch-table"},
    ),
    "0x005a1279": (
        "CFastVB__EvaluateCubicBasisDerivativeVec2",
        "int CFastVB__EvaluateCubicBasisDerivativeVec2(void)",
        ("cubic derivative", "Signature intentionally left unchanged", "locked parameter storage"),
        COMMON_COMMENT_TAGS | {"cubic-derivative", "vec2", "stack-locked", "dispatch-table"},
    ),
    "0x005a13f7": (
        "CFastVB__DispatchOp_InterpolateVec3ByReciprocal_005a13f7",
        "int CFastVB__DispatchOp_InterpolateVec3ByReciprocal_005a13f7(void)",
        ("reciprocal-weighted", "Signature intentionally left unchanged", "locked parameter storage"),
        COMMON_COMMENT_TAGS | {"interpolate", "vec3", "reciprocal", "stack-locked", "dispatch-table"},
    ),
    "0x005a14a5": (
        "CFastVB__DispatchOp_BuildPlaneFromTriangle_005a14a5",
        "void __stdcall CFastVB__DispatchOp_BuildPlaneFromTriangle_005a14a5(float * out_plane_vec4, float * point_a_vec3, float * point_b_vec3, float * point_c_vec3)",
        ("plane-from-triangle", "cross-product", "RET 0x10"),
        COMMON_SIGNATURE_TAGS | {"plane", "triangle", "cross-product", "normalize", "dispatch-table"},
    ),
    "0x005a15a5": (
        "CFastVB__DispatchOp_QuaternionToMatrix4_005a15a5",
        "void __stdcall CFastVB__DispatchOp_QuaternionToMatrix4_005a15a5(float * out_matrix4x4, float * quaternion_xyzw)",
        ("quaternion-to-matrix4", "sixteen matrix floats", "RET 0x8"),
        COMMON_SIGNATURE_TAGS | {"quaternion", "matrix4x4", "normalize", "dispatch-table"},
    ),
    "0x005a16b1": (
        "CFastVB__DispatchOp_TransformVec3ByMatrix4_005a16b1",
        "void __stdcall CFastVB__DispatchOp_TransformVec3ByMatrix4_005a16b1(float * out_vec3, float * input_vec3, float * matrix4x4)",
        ("scalar Vec3-by-matrix4", "batch tails", "RET 0xc"),
        COMMON_SIGNATURE_TAGS | {"vec3", "matrix4x4", "transform", "tail-scalar-dispatch", "dispatch-table"},
    ),
    "0x005a1786": (
        "CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a1786",
        "void __stdcall CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a1786(float * out_projected_vec3, float * input_vec3, float * matrix4x4)",
        ("scalar projected Vec3", "rcpps", "RET 0xc"),
        COMMON_SIGNATURE_TAGS | {"vec3", "matrix4x4", "projective-transform", "reciprocal", "dispatch-table"},
    ),
    "0x005a1889": (
        "CFastVB__DispatchOp_NormalizeVec3_005a1889",
        "void __stdcall CFastVB__DispatchOp_NormalizeVec3_005a1889(float * out_vec3, float * input_vec3)",
        ("scalar Vec3 normalization", "tiny length-square", "RET 0x8"),
        COMMON_SIGNATURE_TAGS | {"vec3", "normalize", "reciprocal-sqrt", "dispatch-table"},
    ),
    "0x005a1979": (
        "CFastVB__DispatchOp_NormalizeVec4_005a1979",
        "void __stdcall CFastVB__DispatchOp_NormalizeVec4_005a1979(float * out_vec4, float * input_vec4)",
        ("scalar Vec4 normalization", "fourth lane", "RET 0x8"),
        COMMON_SIGNATURE_TAGS | {"vec4", "normalize", "reciprocal-sqrt", "dispatch-table"},
    ),
    "0x005a1a8e": (
        "CFastVB__BuildMatrix4x4FromQuaternion",
        "void __stdcall CFastVB__BuildMatrix4x4FromQuaternion(float * out_matrix4x4, float * basis_matrix4x4, float * quaternion_xyzw)",
        ("matrix4x4 build/update", "lazy constants", "RET 0xc"),
        COMMON_SIGNATURE_TAGS | {"matrix4x4", "quaternion", "basis-transform", "normalize", "dispatch-table", "tranche-tail"},
    ),
}

DOC_TOKENS = (
    "Wave718 CFastVB scalar transform core",
    "cfastvb-scalar-transform-core-wave718",
    "0x005a0b22 CFastVB__ConvertHalfToFloatArray_SSE",
    "0x005a0f50 CFastVB__EvaluateCubicBasisVec3",
    "0x005a1a8e CFastVB__BuildMatrix4x4FromQuaternion",
    "0x005a298f CFastVB__ConvertHalfToFloatArray_SIMD",
    "0x0042f220 CSPtrSet__Clear",
    r"G:\GhidraBackups\BEA_20260522-025058_post_wave718_cfastvb_scalar_transform_core_verified",
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
        "pre-metadata.tsv": 17,
        "pre-tags.tsv": 17,
        "pre-xrefs.tsv": 33,
        "pre-instructions.tsv": 1581,
        "pre-instructions-wide.tsv": 4505,
        "pre-decompile/index.tsv": 17,
        "post-metadata.tsv": 17,
        "post-tags.tsv": 17,
        "post-xrefs.tsv": 33,
        "post-instructions.tsv": 1581,
        "post-instructions-wide.tsv": 4505,
        "post-decompile/index.tsv": 17,
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
        require("Wave718 static read-back" in comment, f"missing Wave718 comment at {address}", failures)
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
        "apply-dry.log": "SUMMARY: updated=0 skipped=17 renamed=0 would_rename=0 signature_updated=10 comment_only_updated=7 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=17 skipped=0 renamed=0 would_rename=0 signature_updated=10 comment_only_updated=7 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=17 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "pre-metadata.log": "targets=17 found=17 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=17 missing=0",
        "pre-xrefs.log": "Wrote 33 rows",
        "pre-instructions.log": "Wrote 1581 instruction rows",
        "pre-instructions-wide.log": "Wrote 4505 instruction rows",
        "pre-decompile.log": "targets=17 dumped=17 missing=0 failed=0",
        "post-metadata.log": "targets=17 found=17 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=17 missing=0",
        "post-xrefs.log": "Wrote 33 rows",
        "post-instructions.log": "Wrote 1581 instruction rows",
        "post-instructions-wide.log": "Wrote 4505 instruction rows",
        "post-decompile.log": "targets=17 dumped=17 missing=0 failed=0",
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
    require(quality["commentlessFunctionCount"] == 1884, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 1216, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 143, "param count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005a298f", "high-signal head address mismatch", failures)
    require(high_signal["name"] == "CFastVB__ConvertHalfToFloatArray_SIMD", "high-signal head name mismatch", failures)

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
    require(commented == 4214, "commented count mismatch", failures)
    require(strict_clean == 4157, "strict clean-signature proxy mismatch", failures)
    require(raw_head["address"] == "0x0042f220", "raw commentless head address mismatch", failures)
    require(raw_head["name"] == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup["destination"] == r"G:\GhidraBackups\BEA_20260522-025058_post_wave718_cfastvb_scalar_transform_core_verified", "backup destination mismatch", failures)
    require(backup["fileCount"] == 19, "backup file count mismatch", failures)
    require(int(backup["totalBytes"]) == 166267783, "backup byte count mismatch", failures)
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

    require("test:ghidra-cfastvb-scalar-transform-core-wave718" in read_text(PACKAGE_JSON), "missing package script", failures)

    ledgers = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave718 CFastVB scalar transform core" for row in ledgers), "missing Wave718 ledger row", failures)
    require(any(row.get("task") == "Wave718 CFastVB scalar transform core" for row in attempts), "missing Wave718 attempt row", failures)

    tracking = read_json(TRACKING)
    require(tracking["next_attempt_id"] == 20374, "tracking next_attempt_id mismatch", failures)
    require("Wave718 CFastVB scalar transform core" in tracking.get("current_focus", ""), "tracking focus mismatch", failures)


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
        print("Wave718 CFastVB scalar transform core probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave718 CFastVB scalar transform core probe: PASS")
    print(f"Targets: {len(TARGETS)}")
    print("Queue: 6098 total, 4214 commented, 1884 commentless, 1216 undefined, 143 param_N")
    print(r"Backup: G:\GhidraBackups\BEA_20260522-025058_post_wave718_cfastvb_scalar_transform_core_verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
