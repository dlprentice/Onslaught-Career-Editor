#!/usr/bin/env python3
"""Validate Wave720 CFastVB quaternion tail read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave720-cfastvb-quaternion-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cfastvb_quaternion_tail_wave720_2026-05-22.md"
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
    "cfastvb-quaternion-tail-wave720",
    "wave720-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "cfastvb-quaternion-tail",
}

TARGETS = {
    "0x005a38c0": (
        "CFastVB__DispatchOp_TransformVec4ArrayByMatrix4",
        "int CFastVB__DispatchOp_TransformVec4ArrayByMatrix4(void)",
        ("Vec4-array-by-matrix4 dispatch", "element count", "Signature intentionally left unchanged"),
        COMMON_TAGS | {"vec4-array", "matrix4x4", "transform", "dispatch-table", "comment-only", "stack-locked", "hidden-stack-context", "tranche-head"},
    ),
    "0x005a3980": (
        "CFastVB__DispatchOp_TransformVec4ArrayByMatrix4_Alt_005a3980",
        "int CFastVB__DispatchOp_TransformVec4ArrayByMatrix4_Alt_005a3980(void)",
        ("alternate Vec4-array-by-matrix4 dispatch", "same strided output/input/matrix/count shape", "Signature intentionally left unchanged"),
        COMMON_TAGS | {"vec4-array", "matrix4x4", "transform", "dispatch-table", "comment-only", "stack-locked", "hidden-stack-context", "alternate-dispatch"},
    ),
    "0x005a40c0": (
        "CFastVB__DispatchOp_TransformVec3ArrayByMatrix4_WithTranslation_005a40c0",
        "int CFastVB__DispatchOp_TransformVec3ArrayByMatrix4_WithTranslation_005a40c0(void)",
        ("strided Vec3-array-by-matrix4 dispatch", "translation terms", "Signature intentionally left unchanged"),
        COMMON_TAGS | {"vec3-array", "matrix4x4", "translation", "transform", "dispatch-table", "comment-only", "stack-locked", "hidden-stack-context"},
    ),
    "0x005a47f2": (
        "CFastVB__DispatchOp_ExtractAxisAndOptionalAngle",
        "void __stdcall CFastVB__DispatchOp_ExtractAxisAndOptionalAngle(float * quaternion_xyzw, float * out_axis_vec3_or_null, float * out_angle_or_null)",
        ("quaternion axis/angle extraction", "optional axis output", "CFastVB__FastAcosApprox_Scalar"),
        COMMON_TAGS | {"quaternion", "axis-angle", "fast-acos", "optional-output", "dispatch-table", "signature-hardened"},
    ),
    "0x005a4d2c": (
        "CFastVB__DispatchOp_BuildQuaternionFromAxisAngleVector_005a4d2c",
        "void __stdcall CFastVB__DispatchOp_BuildQuaternionFromAxisAngleVector_005a4d2c(float * out_quaternion_xyzw, float * axis_vec3, float angle_radians)",
        ("axis-angle-vector-to-quaternion", "CFastVB__DispatchOp_NormalizeVec3_Packed_005a9a5f", "fast trig pair"),
        COMMON_TAGS | {"quaternion", "axis-angle", "normalize", "fast-trig", "dispatch-table", "signature-hardened"},
    ),
    "0x005a4d98": (
        "CFastVB__DispatchOp_InterpolateQuaternionPairCore_005a4d98",
        "void __stdcall CFastVB__DispatchOp_InterpolateQuaternionPairCore_005a4d98(float * out_quaternion_xyzw, float * from_quaternion_xyzw, float * to_quaternion_xyzw, float blend_ratio)",
        ("quaternion-pair interpolation core", "sign/short-path selection", "writes blended quaternion lanes"),
        COMMON_TAGS | {"quaternion", "blend", "interpolation", "slerp-nlerp-core", "dispatch-table", "signature-hardened"},
    ),
    "0x005a4ecf": (
        "CFastVB__DispatchOp_BlendQuaternionTriple_005a4ecf",
        "int CFastVB__DispatchOp_BlendQuaternionTriple_005a4ecf(void)",
        ("quaternion triple-blend dispatch", "interpolates a base quaternion toward two controls", "Signature intentionally left unchanged"),
        COMMON_TAGS | {"quaternion", "interpolation", "triple-blend", "dispatch-table", "comment-only", "stack-locked", "hidden-stack-context"},
    ),
    "0x005a4f5c": (
        "CFastVB__DispatchOp_BlendQuaternionControlPair_005a4f5c",
        "int CFastVB__DispatchOp_BlendQuaternionControlPair_005a4f5c(void)",
        ("quaternion control-pair blend dispatch", "smoothstep-like ratio", "Signature intentionally left unchanged"),
        COMMON_TAGS | {"quaternion", "interpolation", "control-pair-blend", "dispatch-table", "comment-only", "stack-locked", "hidden-stack-context"},
    ),
    "0x005a5052": (
        "CFastVB__DispatchOp_NormalizeQuaternionWithAcosFallback_005a5052",
        "void __stdcall CFastVB__DispatchOp_NormalizeQuaternionWithAcosFallback_005a5052(float * out_quaternion_xyzw, float * input_quaternion_xyzw)",
        ("quaternion normalization/angle fallback", "CFastVB__FastAcosApprox_Scalar", "CFastVB__FastSinApprox_Scalar_005b8da0"),
        COMMON_TAGS | {"quaternion", "normalize", "fast-acos", "fast-sin", "dispatch-table", "signature-hardened"},
    ),
    "0x005a519e": (
        "CFastVB__DispatchOp_BlendQuaternionSplineSegment_005a519e",
        "int CFastVB__DispatchOp_BlendQuaternionSplineSegment_005a519e(void)",
        ("large quaternion spline-segment blend dispatch", "aligns quaternion signs by distance tests", "Signature intentionally left unchanged"),
        COMMON_TAGS | {"quaternion", "spline-segment", "sign-alignment", "dispatch-table", "comment-only", "stack-locked", "hidden-stack-context", "tranche-tail"},
    ),
}

DOC_TOKENS = (
    "Wave720 CFastVB quaternion tail",
    "cfastvb-quaternion-tail-wave720",
    "0x005a38c0 CFastVB__DispatchOp_TransformVec4ArrayByMatrix4",
    "0x005a47f2 CFastVB__DispatchOp_ExtractAxisAndOptionalAngle",
    "0x005a4d98 CFastVB__DispatchOp_InterpolateQuaternionPairCore_005a4d98",
    "0x005a5052 CFastVB__DispatchOp_NormalizeQuaternionWithAcosFallback_005a5052",
    "0x005a519e CFastVB__DispatchOp_BlendQuaternionSplineSegment_005a519e",
    "0x005a62bf CFastVB__DispatchOp_InitIdentityMatrix4x4_005a62bf",
    "0x0042f220 CSPtrSet__Clear",
    r"G:\GhidraBackups\BEA_20260522-035533_post_wave720_cfastvb_quaternion_tail_verified",
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
        "pre-metadata.tsv": 10,
        "pre-tags.tsv": 10,
        "pre-xrefs.tsv": 16,
        "pre-instructions.tsv": 1130,
        "pre-decompile/index.tsv": 10,
        "post-metadata.tsv": 10,
        "post-tags.tsv": 10,
        "post-xrefs.tsv": 16,
        "post-instructions.tsv": 1130,
        "post-instructions-wide.tsv": 3530,
        "post-decompile/index.tsv": 10,
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
        require("Wave720 static read-back" in comment, f"missing Wave720 comment at {address}", failures)
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
        "apply-dry.log": "SUMMARY: updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=4 comment_only_updated=6 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=10 skipped=0 renamed=0 would_rename=0 signature_updated=4 comment_only_updated=6 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "pre-metadata.log": "targets=10 found=10 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "pre-xrefs.log": "Wrote 16 rows",
        "pre-instructions.log": "Wrote 1130 instruction rows",
        "pre-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "post-metadata.log": "targets=10 found=10 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "post-xrefs.log": "Wrote 16 rows",
        "post-instructions.log": "Wrote 1130 instruction rows",
        "post-instructions-wide.log": "Wrote 3530 instruction rows",
        "post-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
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
    require(quality["commentlessFunctionCount"] == 1862, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 1216, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 127, "param count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005a62bf", "high-signal head address mismatch", failures)
    require(high_signal["name"] == "CFastVB__DispatchOp_InitIdentityMatrix4x4_005a62bf", "high-signal head name mismatch", failures)

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
    require(commented == 4236, "commented count mismatch", failures)
    require(strict_clean == 4179, "strict clean-signature proxy mismatch", failures)
    require(raw_head["address"] == "0x0042f220", "raw commentless head address mismatch", failures)
    require(raw_head["name"] == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup["destination"] == r"G:\GhidraBackups\BEA_20260522-035533_post_wave720_cfastvb_quaternion_tail_verified", "backup destination mismatch", failures)
    require(backup["fileCount"] == 19, "backup file count mismatch", failures)
    require(int(backup["totalBytes"]) == 166431623, "backup byte count mismatch", failures)
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

    require("test:ghidra-cfastvb-quaternion-tail-wave720" in read_text(PACKAGE_JSON), "missing package script", failures)

    ledgers = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave720 CFastVB quaternion tail" for row in ledgers), "missing Wave720 ledger row", failures)
    require(any(row.get("attempt_id") == 20375 and row.get("task") == "Wave720 CFastVB quaternion tail" for row in attempts), "missing Wave720 attempt row", failures)

    tracking = read_json(TRACKING)
    require(tracking["next_attempt_id"] == 20376, "tracking next_attempt_id mismatch", failures)
    require("Wave720 CFastVB quaternion tail" in tracking.get("current_focus", ""), "tracking focus mismatch", failures)


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
        print("Wave720 CFastVB quaternion tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave720 CFastVB quaternion tail probe: PASS")
    print(f"Targets: {len(TARGETS)}")
    print("Queue: 6098 total, 4236 commented, 1862 commentless, 1216 undefined, 127 param_N")
    print(r"Backup: G:\GhidraBackups\BEA_20260522-035533_post_wave720_cfastvb_quaternion_tail_verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
