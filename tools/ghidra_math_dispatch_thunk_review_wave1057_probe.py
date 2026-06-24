#!/usr/bin/env python3
"""Validate Wave1057 math dispatch thunk review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1057-math-dispatch-thunk-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_math_dispatch_thunk_review_wave1057_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1057_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
MATH_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Math.cpp" / "_index.md"
FASTVB_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
TEXTURE_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "texture.cpp" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260601-184232_post_wave1057_math_dispatch_thunk_review_verified"

TARGETS = {
    "0x005771af": ("Math__BuildScaleMatrix4x4_Dispatch", "void __stdcall Math__BuildScaleMatrix4x4_Dispatch(void * out_matrix4x4, float scale_x, float scale_y, float scale_z)"),
    "0x005771dd": ("Math__BuildScaleMatrix4x4", "void __stdcall Math__BuildScaleMatrix4x4(void * out_matrix4x4, float scale_x, float scale_y, float scale_z)"),
    "0x00577239": ("Math__BuildTranslationMatrix4x4_Dispatch", "void __stdcall Math__BuildTranslationMatrix4x4_Dispatch(void * out_matrix4x4, float translate_x, float translate_y, float translate_z)"),
    "0x00577267": ("Math__BuildTranslationMatrix4x4_Dispatch_Thunk", "void __stdcall Math__BuildTranslationMatrix4x4_Dispatch_Thunk(void * out_matrix4x4, float translate_x, float translate_y, float translate_z)"),
    "0x0057726d": ("Math__BuildTranslationMatrix4x4", "void __stdcall Math__BuildTranslationMatrix4x4(void * out_matrix4x4, float translate_x, float translate_y, float translate_z)"),
    "0x005772c9": ("Math__BuildRotationMatrixX_Dispatch", "void __stdcall Math__BuildRotationMatrixX_Dispatch(void * out_matrix4x4, float angle_radians)"),
    "0x005772e5": ("Math__BuildRotationMatrixX", "void __stdcall Math__BuildRotationMatrixX(void * out_matrix4x4, float angle_radians)"),
    "0x0057735f": ("Math__BuildRotationMatrixY_Dispatch", "void __stdcall Math__BuildRotationMatrixY_Dispatch(void * out_matrix4x4, float angle_radians)"),
    "0x0057737b": ("Math__BuildRotationMatrixY", "void __stdcall Math__BuildRotationMatrixY(void * out_matrix4x4, float angle_radians)"),
    "0x005773f6": ("Math__BuildRotationMatrixZ_Dispatch", "void __stdcall Math__BuildRotationMatrixZ_Dispatch(void * out_matrix4x4, float angle_radians)"),
    "0x00577412": ("Math__BuildRotationMatrixZ", "void __stdcall Math__BuildRotationMatrixZ(void * out_matrix4x4, float angle_radians)"),
    "0x0057748e": ("Math__BuildAxisAngleRotationMatrix_Dispatch", "void __stdcall Math__BuildAxisAngleRotationMatrix_Dispatch(void * out_matrix4x4, void * axis_vec3, float angle_radians)"),
    "0x005774ae": ("Math__BuildAxisAngleRotationMatrix", "void __stdcall Math__BuildAxisAngleRotationMatrix(void * out_matrix4x4, void * axis_vec3, float angle_radians)"),
    "0x005775b0": ("Math__BuildQuaternionRotationMatrix_Dispatch", "void __stdcall Math__BuildQuaternionRotationMatrix_Dispatch(void * out_matrix4x4, void * quaternion_xyzw)"),
    "0x005775bd": ("Math__BuildQuaternionRotationMatrix_Dispatch_Thunk", "void __stdcall Math__BuildQuaternionRotationMatrix_Dispatch_Thunk(void * out_matrix4x4, void * quaternion_xyzw)"),
    "0x005775c3": ("Math__BuildQuaternionRotationMatrix", "void __stdcall Math__BuildQuaternionRotationMatrix(void * out_matrix4x4, void * quaternion_xyzw)"),
    "0x0057798e": ("CFastVB__BuildAxisAngleQuaternion_Dispatch", "float * __stdcall CFastVB__BuildAxisAngleQuaternion_Dispatch(void * out_quaternion_xyzw, void * axis_vec3, float angle_radians)"),
    "0x005779ae": ("CFastVB__BuildAxisAngleQuaternion", "float * __stdcall CFastVB__BuildAxisAngleQuaternion(void * out_quaternion_xyzw, void * axis_vec3, float angle_radians)"),
    "0x00577a0a": ("Math__BuildQuaternionFromEulerAngles_Dispatch", "void __stdcall Math__BuildQuaternionFromEulerAngles_Dispatch(void * out_quaternion_xyzw, float angle_x, float angle_y, float angle_z)"),
    "0x00577a38": ("Math__BuildQuaternionFromEulerAngles_Dispatch_Thunk", "void __stdcall Math__BuildQuaternionFromEulerAngles_Dispatch_Thunk(void * out_quaternion_xyzw, float angle_x, float angle_y, float angle_z)"),
    "0x00577a3e": ("Math__BuildQuaternionFromEulerAngles", "void __stdcall Math__BuildQuaternionFromEulerAngles(void * out_quaternion_xyzw, float angle_x, float angle_y, float angle_z)"),
    "0x00577e80": ("Math__InterpolateVec4ByRatio_Dispatch", "void __stdcall Math__InterpolateVec4ByRatio_Dispatch(void * out_vec4, void * from_vec4, void * to_vec4, float ratio)"),
    "0x00577ea4": ("Math__InterpolateVec4ByRatio_Dispatch_Thunk", "void __stdcall Math__InterpolateVec4ByRatio_Dispatch_Thunk(void * out_vec4, void * from_vec4, void * to_vec4, float ratio)"),
    "0x00577eaa": ("Math__InterpolateVec4ByRatio", "void __stdcall Math__InterpolateVec4ByRatio(void * out_vec4, void * from_vec4, void * to_vec4, float ratio)"),
}

CONTEXT_NAMES = {
    "0x00575986": "Math__IsFloatDiffOutsideTolerance",
    "0x005776a5": "CTexture__DispatchPtr00656fd0_WithInit",
    "0x0057804e": "Math__BlendVec4DualWeights",
    "0x00579184": "CFastVB__NormalizeQuaternionCopy",
    "0x0058926b": "CFastVB__InitDispatchTableByCpuFeature",
    "0x00596341": "CFastVB__InitMathDispatchTable",
    "0x005980be": "CFastVB__InitDispatchTableVariant_005980be",
    "0x0059822c": "CFastVB__InitDispatchTableVariant_0059822c",
    "0x00598474": "CFastVB__InitDispatchOpsFromFeatureFlags",
}

EXPECTED_DATA_XREFS = {
    "0x005771af": "0x00656fb4",
    "0x005771dd": "0x006570d4",
    "0x00577239": "0x00656f98",
    "0x0057726d": "0x006570b8",
    "0x005772c9": "0x00656fa8",
    "0x005772e5": "0x006570c8",
    "0x0057735f": "0x00656fac",
    "0x0057737b": "0x006570cc",
    "0x005773f6": "0x00656fb0",
    "0x00577412": "0x006570d0",
    "0x0057748e": "0x00656fd8",
    "0x005774ae": "0x006570f8",
    "0x005775c3": "0x006570e8",
    "0x0057798e": "0x00656fa4",
    "0x005779ae": "0x006570c4",
    "0x00577a0a": "0x00656f94",
    "0x00577a3e": "0x006570b4",
    "0x00577e80": "0x00656fbc",
    "0x00577eaa": "0x006570dc",
}

DOC_TOKENS = (
    "Wave1057",
    "math-dispatch-thunk-review-wave1057",
    "0x005771af Math__BuildScaleMatrix4x4_Dispatch",
    "0x005771dd Math__BuildScaleMatrix4x4",
    "0x00577239 Math__BuildTranslationMatrix4x4_Dispatch",
    "0x005775c3 Math__BuildQuaternionRotationMatrix",
    "0x0057798e CFastVB__BuildAxisAngleQuaternion_Dispatch",
    "0x00577a3e Math__BuildQuaternionFromEulerAngles",
    "0x00577eaa Math__InterpolateVec4ByRatio",
    "CFastVB__InitDispatchTableByCpuFeature",
    "CFastVB__InitMathDispatchTable",
    "CFastVB__InitDispatchTableVariant_005980be",
    "CFastVB__InitDispatchOpsFromFeatureFlags",
    "799/1408 = 56.75%",
    "1121/1509 = 74.29%",
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
        "metadata.tsv": 24,
        "tags.tsv": 24,
        "xrefs.tsv": 46,
        "instructions.tsv": 703,
        "decompile/index.tsv": 24,
        "context-metadata.tsv": 24,
        "context-tags.tsv": 24,
        "context-xrefs.tsv": 116,
        "context-instructions.tsv": 499,
        "context-decompile/index.tsv": 24,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "xrefs.tsv")

    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            require("Static retail" in row.get("comment", ""), f"missing static-boundary wording at {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require("static-reaudit" in actual_tags, f"missing static-reaudit tag at {address}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    for address, expected_from in EXPECTED_DATA_XREFS.items():
        matches = [
            row
            for row in xrefs
            if normalize_address(row.get("target_addr", "")) == address
            and normalize_address(row.get("from_addr", "")) == expected_from
            and row.get("ref_type") == "DATA"
        ]
        require(matches, f"missing DATA xref for {address} from {expected_from}", failures)

    context = {normalize_address(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}
    for address, name in CONTEXT_NAMES.items():
        row = context.get(address)
        require(row is not None, f"missing context metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"context name mismatch at {address}", failures)
            require(row.get("status") == "OK", f"context status mismatch at {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "metadata.log": "targets=24 found=24 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=24 missing=0",
        "xrefs.log": "Wrote 46 rows",
        "instructions.log": "Wrote 703 function-body instruction rows",
        "decompile.log": "targets=24 dumped=24 missing=0 failed=0",
        "context-metadata.log": "targets=24 found=24 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=24 missing=0",
        "context-xrefs.log": "Wrote 116 rows",
        "context-instructions.log": "Wrote 499 function-body instruction rows",
        "context-decompile.log": "targets=24 dumped=24 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR", "BADNAME", "FAIL:", "missing=1", "bad=1", "failed=1"):
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
    require(all(row.get("comment", "").strip() for row in rows), "quality TSV has commentless row", failures)
    require(all(not row.get("signature", "").startswith("undefined ") for row in rows), "quality TSV has undefined signature", failures)
    require(
        all(not re.search(r"\bparam_\d+\b", row.get("signature", "")) for row in rows),
        "quality TSV has param_N signature",
        failures,
    )

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 174656391 or backup.get("totalBytes") == 174656391.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        PUBLIC_NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        MATH_INDEX,
        FASTVB_INDEX,
        TEXTURE_INDEX,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-math-dispatch-thunk-review-wave1057")
        == r"py -3 tools\ghidra_math_dispatch_thunk_review_wave1057_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1057-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1057 --check",
        "missing aggregate package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1057 math dispatch thunk review" for row in ledger_rows), "missing Wave1057 ledger row", failures)
    require(any(row.get("task") == "Wave1057 math dispatch thunk review" and row.get("attempt_id") == 20639 for row in attempts), "missing Wave1057 attempt row", failures)


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
        print("Wave1057 math dispatch thunk review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1057 math dispatch thunk review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
