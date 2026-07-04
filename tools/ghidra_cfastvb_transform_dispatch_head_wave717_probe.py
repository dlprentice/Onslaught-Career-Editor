#!/usr/bin/env python3
"""Validate Wave717 CFastVB transform dispatch head read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave717-cfastvb-transform-dispatch-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cfastvb_transform_dispatch_head_wave717_2026-05-22.md"
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

SIGNATURE_TAGS = {
    "static-reaudit",
    "cfastvb-transform-dispatch-head-wave717",
    "wave717-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "cfastvb-transform-dispatch-head",
}

COMMENT_ONLY_TAGS = {
    "static-reaudit",
    "cfastvb-transform-dispatch-head-wave717",
    "wave717-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "comment-only",
    "hidden-register-context",
    "cfastvb-transform-dispatch-head",
}

TARGETS = {
    "0x0059f360": (
        "CFastVB__DispatchOp_TransformVec4_0059f360",
        "int __stdcall CFastVB__DispatchOp_TransformVec4_0059f360(void * out_vec4, void * input_vec4, void * matrix4x4)",
        ("transforms input_vec4", "RET 0xc", "InitDispatchTableVariant"),
        SIGNATURE_TAGS | {"simd", "matrix4x4", "vec4", "transform", "dispatch-table", "tranche-head"},
    ),
    "0x0059f3d9": (
        "CFastVB__DispatchOp_NormalizeVec4_0059f3d9",
        "float * __stdcall CFastVB__DispatchOp_NormalizeVec4_0059f3d9(void * out_vec4, void * input_vec4)",
        ("vec4 length square", "rsqrtss", "RET 0x8"),
        SIGNATURE_TAGS | {"simd", "vec4", "normalize", "reciprocal-sqrt", "dispatch-table"},
    ),
    "0x0059f473": (
        "CFastVB__DispatchOp_NormalizeVec4Scaled_0059f473",
        "void __stdcall CFastVB__DispatchOp_NormalizeVec4Scaled_0059f473(void * out_vec4, void * input_vec4)",
        ("normalizes input_vec4", "0x0065e500", "RET 0x8"),
        SIGNATURE_TAGS | {"simd", "vec4", "normalize", "scaled", "dispatch-table"},
    ),
    "0x0059f4f1": (
        "CFastVB__DispatchOp_EulerToQuaternion_0059f4f1",
        "void __stdcall CFastVB__DispatchOp_EulerToQuaternion_0059f4f1(void * out_quaternion_xyzw, float angle_x_radians, float angle_y_radians, float angle_z_radians)",
        ("Euler", "SinCosApproxVec4_Paired", "RET 0x10"),
        SIGNATURE_TAGS | {"simd", "quaternion", "euler", "dispatch-table"},
    ),
    "0x0059f5b3": (
        "CFastVB__BuildOrthonormalBasisFromCovariance",
        "void __stdcall CFastVB__BuildOrthonormalBasisFromCovariance(void * out_quaternion_xyzw, void * matrix3x3_or_basis)",
        ("matrix trace", "maximum diagonal", "matrix3x3_or_basis"),
        SIGNATURE_TAGS | {"simd-adjacent", "quaternion", "matrix3x3", "trace-branch", "dispatch-table"},
    ),
    "0x0059f6dd": (
        "CFastVB__BroadcastMatrix4x4ToSIMDLanes",
        "void __thiscall CFastVB__BroadcastMatrix4x4ToSIMDLanes(void * this, void * simd_lane_matrix_out, void * matrix4x4)",
        ("broadcasts each source matrix4x4", "RET 0x4", "thiscall normalization mismatch"),
        SIGNATURE_TAGS | {"simd", "matrix4x4", "lane-broadcast", "batch-transform"},
    ),
    "0x0059f857": (
        "CFastVB__DispatchOp_TransformVec4Batch_0059f857",
        "int CFastVB__DispatchOp_TransformVec4Batch_0059f857(void)",
        ("Signature intentionally left unchanged", "hidden EDI context", "TransformVec4ByMatrix4"),
        COMMENT_ONLY_TAGS | {"simd", "matrix4x4", "vec4", "batch-transform", "tail-scalar-dispatch"},
    ),
    "0x0059fa5d": (
        "CFastVB__DispatchOp_TransformVec4BatchW_0059fa5d",
        "int CFastVB__DispatchOp_TransformVec4BatchW_0059fa5d(void)",
        ("Signature intentionally left unchanged", "hidden EBX/EDI context", "dispatch slot"),
        COMMENT_ONLY_TAGS | {"simd", "matrix4x4", "vec4", "batch-transform", "hidden-ebx-context", "tail-dispatch"},
    ),
    "0x0059fbeb": (
        "CFastVB__DispatchOp_TransformProjectVec4Batch_0059fbeb",
        "int CFastVB__DispatchOp_TransformProjectVec4Batch_0059fbeb(void)",
        ("Signature intentionally left unchanged", "reciprocal projection", "hidden EBX/EDI context"),
        COMMENT_ONLY_TAGS | {"simd", "matrix4x4", "vec4", "perspective-transform", "batch-transform", "hidden-ebx-context"},
    ),
    "0x0059fd51": (
        "CFastVB__DispatchOp_TransformVec4Batch_NoOffset_0059fd51",
        "int CFastVB__DispatchOp_TransformVec4Batch_NoOffset_0059fd51(void)",
        ("Signature intentionally left unchanged", "no-offset", "hidden EBX/EDI context"),
        COMMENT_ONLY_TAGS | {"simd", "matrix4x4", "vec4", "batch-transform", "no-offset", "hidden-ebx-context"},
    ),
    "0x0059fe61": (
        "CFastVB__DispatchOp_TransformVec4Batch_Perspective_0059fe61",
        "int CFastVB__DispatchOp_TransformVec4Batch_Perspective_0059fe61(void)",
        ("Signature intentionally left unchanged", "perspective-flavored", "TransformVec2ByMatrix4"),
        COMMENT_ONLY_TAGS | {"simd", "matrix4x4", "vec4", "perspective-transform", "batch-transform", "tail-scalar-dispatch"},
    ),
    "0x005a009f": (
        "CFastVB__DispatchOp_TransformVec3WBatch_005a009f",
        "int CFastVB__DispatchOp_TransformVec3WBatch_005a009f(void)",
        ("Signature intentionally left unchanged", "Vec3W", "TransformVec3ByMatrix4"),
        COMMENT_ONLY_TAGS | {"simd", "matrix4x4", "vec3", "batch-transform", "tail-scalar-dispatch"},
    ),
    "0x005a026f": (
        "CFastVB__DispatchOp_TransformProjectVec3WBatch_005a026f",
        "int CFastVB__DispatchOp_TransformProjectVec3WBatch_005a026f(void)",
        ("Signature intentionally left unchanged", "projected Vec3W", "TransformProjectVec3ByMatrix4"),
        COMMENT_ONLY_TAGS | {"simd", "matrix4x4", "vec3", "perspective-transform", "batch-transform", "tail-scalar-dispatch"},
    ),
    "0x005a04a0": (
        "CFastVB__DispatchOp_WeightedMatrixBlendBatch_005a04a0",
        "int CFastVB__DispatchOp_WeightedMatrixBlendBatch_005a04a0(void)",
        ("Signature intentionally left unchanged", "weighted matrix", "large stack-argument contract"),
        COMMENT_ONLY_TAGS | {"simd", "matrix4x4", "weighted-blend", "batch-transform", "auxiliary-vector-output", "tranche-tail"},
    ),
}

DOC_TOKENS = (
    "Wave717 CFastVB transform dispatch head",
    "cfastvb-transform-dispatch-head-wave717",
    "0x0059f360 CFastVB__DispatchOp_TransformVec4_0059f360",
    "0x0059f6dd CFastVB__BroadcastMatrix4x4ToSIMDLanes",
    "0x005a04a0 CFastVB__DispatchOp_WeightedMatrixBlendBatch_005a04a0",
    "Ghidra thiscall normalization mismatch",
    "0x005a0b22 CFastVB__ConvertHalfToFloatArray_SSE",
    "0x0042f220 CSPtrSet__Clear",
    r"[maintainer-local-ghidra-backup-root]\BEA_20260522-021449_post_wave717_cfastvb_transform_dispatch_head_verified",
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
        "pre-metadata.tsv": 14,
        "pre-tags.tsv": 14,
        "pre-xrefs.tsv": 32,
        "pre-instructions.tsv": 1246,
        "pre-instructions-wide.tsv": 3654,
        "pre-decompile/index.tsv": 14,
        "post-metadata.tsv": 14,
        "post-tags.tsv": 14,
        "post-xrefs.tsv": 32,
        "post-instructions.tsv": 1246,
        "post-instructions-wide.tsv": 3766,
        "post-decompile/index.tsv": 14,
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
        require("Wave717 static read-back" in comment, f"missing Wave717 comment at {address}", failures)
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
        "apply-dry.log": "SUMMARY: updated=0 skipped=14 renamed=0 would_rename=0 signature_updated=6 comment_only_updated=8 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=13 skipped=0 renamed=0 would_rename=0 signature_updated=5 comment_only_updated=8 missing=0 bad=1",
        "apply-corrected-dry.log": "SUMMARY: updated=0 skipped=14 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "apply-corrected.log": "SUMMARY: updated=1 skipped=13 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=14 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "pre-metadata.log": "targets=14 found=14 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=14 missing=0",
        "pre-xrefs.log": "Wrote 32 rows",
        "pre-instructions.log": "Wrote 1246 instruction rows",
        "pre-instructions-wide.log": "Wrote 3654 instruction rows",
        "pre-decompile.log": "targets=14 dumped=14 missing=0 failed=0",
        "post-metadata.log": "targets=14 found=14 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=14 missing=0",
        "post-xrefs.log": "Wrote 32 rows",
        "post-instructions.log": "Wrote 1246 instruction rows",
        "post-instructions-wide.log": "Wrote 3766 instruction rows",
        "post-decompile.log": "targets=14 dumped=14 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}", failures)
        require("LockException" not in text, f"unexpected LockException in {relative}", failures)
        require("MISSING:" not in text, f"unexpected MISSING in {relative}", failures)

    first_apply = read_text(BASE / "apply.log")
    require("BAD: 0x0059f6dd CFastVB__BroadcastMatrix4x4ToSIMDLanes" in first_apply, "missing preserved first apply BAD evidence", failures)
    require("Read-back signature mismatch" in first_apply, "missing first apply read-back mismatch", failures)
    require("REPORT: Save succeeded" in first_apply, "missing first apply save evidence", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 1901, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 1216, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 153, "param count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005a0b22", "high-signal head address mismatch", failures)
    require(high_signal["name"] == "CFastVB__ConvertHalfToFloatArray_SSE", "high-signal head name mismatch", failures)

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
    require(commented == 4197, "commented count mismatch", failures)
    require(strict_clean == 4140, "strict clean-signature proxy mismatch", failures)
    require(raw_head["address"] == "0x0042f220", "raw commentless head address mismatch", failures)
    require(raw_head["name"] == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup["destination"] == r"[maintainer-local-ghidra-backup-root]\BEA_20260522-021449_post_wave717_cfastvb_transform_dispatch_head_verified", "backup destination mismatch", failures)
    require(backup["fileCount"] == 19, "backup file count mismatch", failures)
    require(int(backup["totalBytes"]) == 166235015, "backup byte count mismatch", failures)
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

    require("test:ghidra-cfastvb-transform-dispatch-head-wave717" in read_text(PACKAGE_JSON), "missing package script", failures)

    ledgers = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave717 CFastVB transform dispatch head" for row in ledgers), "missing Wave717 ledger row", failures)
    require(any(row.get("task") == "Wave717 CFastVB transform dispatch head" for row in attempts), "missing Wave717 attempt row", failures)

    tracking = read_json(TRACKING)
    require(tracking["next_attempt_id"] == 20373, "tracking next_attempt_id mismatch", failures)
    require("Wave717 CFastVB transform dispatch head" in tracking.get("current_focus", ""), "tracking focus mismatch", failures)


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
        print("Wave717 CFastVB transform dispatch head probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave717 CFastVB transform dispatch head probe: PASS")
    print(f"Targets: {len(TARGETS)}")
    print("Queue: 6098 total, 4197 commented, 1901 commentless, 1216 undefined, 153 param_N")
    print(r"Backup: [maintainer-local-ghidra-backup-root]\BEA_20260522-021449_post_wave717_cfastvb_transform_dispatch_head_verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
