#!/usr/bin/env python3
"""Validate Wave660 math dispatch read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave660-math-dispatch-continuation"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_math_dispatch_wave660_2026-05-21.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
MATH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Math.cpp" / "_index.md"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
TEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "texture.cpp" / "_index.md"
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
BACKUP_SUMMARY = BASE / "backup-summary.json"

COMMON_TAGS = {
    "static-reaudit",
    "math-dispatch-wave660",
    "retail-binary-evidence",
    "signature-hardened",
    "comment-hardened",
}

TARGETS = {
    "0x005776a5": {
        "name": "CTexture__DispatchPtr00656fd0_WithInit",
        "signature": "void __stdcall CTexture__DispatchPtr00656fd0_WithInit(int slot_arg0, int slot_arg1, int slot_arg2, int slot_arg3)",
        "tags": {"dispatch-table", "deferred-contract"},
        "comment_tokens": ("runtime dispatch-table slot 40", "0x00656fd0", "source/default slot 40"),
        "decompile": "005776a5_CTexture__DispatchPtr00656fd0_WithInit.c",
    },
    "0x0057798e": {
        "name": "CFastVB__BuildAxisAngleQuaternion_Dispatch",
        "signature": "float * __stdcall CFastVB__BuildAxisAngleQuaternion_Dispatch(void * out_quaternion_xyzw, void * axis_vec3, float angle_radians)",
        "tags": {"dispatch-table", "quaternion", "axis-angle"},
        "comment_tokens": ("runtime dispatch-table slot 29", "0x00656fa4", "0x005779ae"),
        "decompile": "0057798e_CFastVB__BuildAxisAngleQuaternion_Dispatch.c",
    },
    "0x005779ae": {
        "name": "CFastVB__BuildAxisAngleQuaternion",
        "signature": "float * __stdcall CFastVB__BuildAxisAngleQuaternion(void * out_quaternion_xyzw, void * axis_vec3, float angle_radians)",
        "tags": {"source-dispatch-table", "quaternion", "axis-angle"},
        "comment_tokens": ("source/default dispatch-table slot 29", "0x006570c4", "FSIN/FCOS"),
        "decompile": "005779ae_CFastVB__BuildAxisAngleQuaternion.c",
    },
    "0x00577a0a": {
        "name": "Math__BuildEulerRotationMatrix4x4_Dispatch",
        "signature": "void __stdcall Math__BuildEulerRotationMatrix4x4_Dispatch(void * out_matrix4x4, float angle_x_radians, float angle_y_radians, float angle_z_radians)",
        "tags": {"dispatch-table", "matrix4x4", "rotation-matrix", "euler"},
        "comment_tokens": ("runtime dispatch-table slot 25", "0x00656f94", "0x00577a3e"),
        "decompile": "00577a0a_Math__BuildEulerRotationMatrix4x4_Dispatch.c",
    },
    "0x00577a38": {
        "name": "Math__BuildEulerRotationMatrix4x4_Dispatch_Thunk",
        "signature": "void __stdcall Math__BuildEulerRotationMatrix4x4_Dispatch_Thunk(void * out_matrix4x4, float angle_x_radians, float angle_y_radians, float angle_z_radians)",
        "tags": {"dispatch-table", "matrix4x4", "rotation-matrix", "euler", "jump-thunk"},
        "comment_tokens": ("pure jump thunk", "runtime dispatch-table slot 25", "0x00656f94"),
        "decompile": "00577a38_Math__BuildEulerRotationMatrix4x4_Dispatch_Thunk.c",
    },
    "0x00577a3e": {
        "name": "Math__BuildEulerRotationMatrix4x4",
        "signature": "void __stdcall Math__BuildEulerRotationMatrix4x4(void * out_matrix4x4, float angle_x_radians, float angle_y_radians, float angle_z_radians)",
        "tags": {"source-dispatch-table", "boundary-recovered", "matrix4x4", "rotation-matrix", "euler"},
        "comment_tokens": ("source/default dispatch-table slot 25", "RET 0x10 at 0x00577b14", "FSINCOS"),
        "decompile": "00577a3e_Math__BuildEulerRotationMatrix4x4.c",
    },
    "0x00577e80": {
        "name": "Math__InterpolateVec4ByRatio_Dispatch",
        "signature": "void __stdcall Math__InterpolateVec4ByRatio_Dispatch(void * out_vec4, void * from_vec4, void * to_vec4, float ratio)",
        "tags": {"dispatch-table", "vec4", "interpolation"},
        "comment_tokens": ("runtime dispatch-table slot 35", "0x00656fbc", "0x00577eaa"),
        "decompile": "00577e80_Math__InterpolateVec4ByRatio_Dispatch.c",
    },
    "0x00577ea4": {
        "name": "Math__InterpolateVec4ByRatio_Dispatch_Thunk",
        "signature": "void __stdcall Math__InterpolateVec4ByRatio_Dispatch_Thunk(void * out_vec4, void * from_vec4, void * to_vec4, float ratio)",
        "tags": {"dispatch-table", "vec4", "interpolation", "jump-thunk"},
        "comment_tokens": ("pure jump thunk", "runtime dispatch-table slot 35", "0x00656fbc"),
        "decompile": "00577ea4_Math__InterpolateVec4ByRatio_Dispatch_Thunk.c",
    },
    "0x00577eaa": {
        "name": "Math__InterpolateVec4ByRatio",
        "signature": "void __stdcall Math__InterpolateVec4ByRatio(void * out_vec4, void * from_vec4, void * to_vec4, float ratio)",
        "tags": {"source-dispatch-table", "boundary-recovered", "vec4", "interpolation"},
        "comment_tokens": ("source/default dispatch-table slot 35", "RET 0x10 at 0x00577f8a", "sine-weighted"),
        "decompile": "00577eaa_Math__InterpolateVec4ByRatio.c",
    },
    "0x00577f8d": {
        "name": "Math__BezierBlendVec4_Dispatch",
        "signature": "void * __stdcall Math__BezierBlendVec4_Dispatch(void * out_vec4, void * control0_vec4, void * control1_vec4, void * control2_vec4, void * control3_vec4, float ratio)",
        "tags": {"dispatch-table", "vec4", "bezier"},
        "comment_tokens": ("runtime dispatch-table slot 43", "0x00656fdc", "0x00577fb7"),
        "decompile": "00577f8d_Math__BezierBlendVec4_Dispatch.c",
    },
    "0x00577fb7": {
        "name": "Math__BezierBlendVec4",
        "signature": "void * __stdcall Math__BezierBlendVec4(void * out_vec4, void * control0_vec4, void * control1_vec4, void * control2_vec4, void * control3_vec4, float ratio)",
        "tags": {"source-dispatch-table", "vec4", "bezier"},
        "comment_tokens": ("source/default dispatch-table slot 43", "three interpolation calls", "control0_vec4"),
        "decompile": "00577fb7_Math__BezierBlendVec4.c",
    },
    "0x0057804e": {
        "name": "Math__BlendVec4DualWeights",
        "signature": "void * __stdcall Math__BlendVec4DualWeights(void * out_vec4, void * base_vec4, void * target_a_vec4, void * target_b_vec4, float weight_a, float weight_b)",
        "tags": {"source-dispatch-table", "vec4", "interpolation", "dual-weight"},
        "comment_tokens": ("source/default dispatch-table slot 36", "weight_b /", "copies base_vec4"),
        "decompile": "0057804e_Math__BlendVec4DualWeights.c",
    },
    "0x00578555": {
        "name": "Math__TransformVec2ByMatrix4x4",
        "signature": "void __stdcall Math__TransformVec2ByMatrix4x4(void * out_vec4, void * input_vec2, void * matrix4x4)",
        "tags": {"source-dispatch-table", "matrix4x4", "vec2", "transform"},
        "comment_tokens": ("source/default dispatch-table slot 0", "0x00657050", "four-float output"),
        "decompile": "00578555_Math__TransformVec2ByMatrix4x4.c",
    },
    "0x00578643": {
        "name": "Math__TransformVec2ByMatrixPerspective",
        "signature": "void __stdcall Math__TransformVec2ByMatrixPerspective(void * out_vec2, void * input_vec2, void * matrix4x4)",
        "tags": {"source-dispatch-table", "matrix4x4", "vec2", "perspective-transform"},
        "comment_tokens": ("source/default dispatch-table slot 9", "0x00657074", "perspective divide"),
        "decompile": "00578643_Math__TransformVec2ByMatrixPerspective.c",
    },
    "0x00578758": {
        "name": "Math__TransformVec2ByMatrixLinear",
        "signature": "void __stdcall Math__TransformVec2ByMatrixLinear(void * out_vec2, void * input_vec2, void * matrix4x4)",
        "tags": {"source-dispatch-table", "matrix4x4", "vec2", "linear-transform"},
        "comment_tokens": ("source/default dispatch-table slot 5", "0x00657064", "linear transform"),
        "decompile": "00578758_Math__TransformVec2ByMatrixLinear.c",
    },
    "0x005787e8": {
        "name": "Math__NormalizeVec3",
        "signature": "void __stdcall Math__NormalizeVec3(void * out_vec3, void * input_vec3)",
        "tags": {"source-dispatch-table", "vec3", "normalize"},
        "comment_tokens": ("source/default dispatch-table slot 7", "0x0065706c", "near-zero"),
        "decompile": "005787e8_Math__NormalizeVec3.c",
    },
    "0x00578885": {
        "name": "Math__TransformVec3ByMatrixPerspective",
        "signature": "void __stdcall Math__TransformVec3ByMatrixPerspective(void * out_vec3, void * input_vec3, void * matrix4x4)",
        "tags": {"source-dispatch-table", "matrix4x4", "vec3", "perspective-transform"},
        "comment_tokens": ("source/default dispatch-table slot 10", "0x00657078", "perspective divide"),
        "decompile": "00578885_Math__TransformVec3ByMatrixPerspective.c",
    },
}

DOC_TOKENS = (
    "Wave660 math dispatch continuation",
    "math-dispatch-wave660",
    "0x005776a5 CTexture__DispatchPtr00656fd0_WithInit",
    "3619",
    "2479",
    "698",
    "3569/6098 = 58.53%",
    "G:\\GhidraBackups\\BEA_20260520-230154_post_wave660_math_dispatch_verified",
    "0x00579184 CFastVB__NormalizeQuaternionCopy",
)

OVERCLAIM_TOKENS = (
    "runtime math correctness proven",
    "exact vector/matrix storage contract proven",
    "CPU feature replacement behavior proven",
    "rebuild parity proven",
    "fully reverse-engineered",
    "fully recovered",
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
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in read_text(path).splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def table_by_slot(path: Path) -> dict[int, dict[str, str]]:
    rows = read_tsv(path)
    return {int(row["slot"]): row for row in rows}


def check_metadata(failures: list[str]) -> None:
    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile_index = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile-post" / "index.tsv")}

    require(len(metadata) == len(TARGETS), f"metadata row count is {len(metadata)}", failures)
    require(len(tags) == len(TARGETS), f"tag row count is {len(tags)}", failures)
    require(len(decompile_index) == len(TARGETS), f"decompile index row count is {len(decompile_index)}", failures)

    for address, expected in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == expected["name"], f"name mismatch at {address}: {row.get('name')}", failures)
        require(row.get("signature") == expected["signature"], f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}: {row.get('status')}", failures)
        comment = row.get("comment", "")
        require("Wave660 math dispatch" in comment, f"missing Wave660 comment at {address}", failures)
        require("runtime math correctness" in comment, f"missing uncertainty clause at {address}", failures)
        for token in expected["comment_tokens"]:
            require(token in comment, f"comment token {token!r} missing at {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"common tags missing at {address}: {actual_tags}", failures)
            require(expected["tags"].issubset(actual_tags), f"specific tags missing at {address}: {actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}: {tag_row.get('status')}", failures)

        decompile_row = decompile_index.get(address)
        require(decompile_row is not None, f"missing decompile index for {address}", failures)
        if decompile_row is not None:
            require(decompile_row.get("signature") == expected["signature"], f"decompile signature mismatch at {address}", failures)
            require(decompile_row.get("status") == "OK", f"decompile status mismatch at {address}", failures)
        require((BASE / "decompile-post" / expected["decompile"]).is_file(), f"missing decompile file {expected['decompile']}", failures)

    require((BASE / "post-xrefs.tsv").is_file(), "missing post-xrefs.tsv", failures)
    require((BASE / "post-instructions.tsv").is_file(), "missing post-instructions.tsv", failures)


def check_dispatch_tables(failures: list[str]) -> None:
    runtime = table_by_slot(BASE / "dispatch-runtime-table-post.tsv")
    source = table_by_slot(BASE / "dispatch-source-table-post.tsv")

    expected_runtime = {
        25: ("00577a0a", "Math__BuildEulerRotationMatrix4x4_Dispatch"),
        29: ("0057798e", "CFastVB__BuildAxisAngleQuaternion_Dispatch"),
        35: ("00577e80", "Math__InterpolateVec4ByRatio_Dispatch"),
        40: ("005776a5", "CTexture__DispatchPtr00656fd0_WithInit"),
        43: ("00577f8d", "Math__BezierBlendVec4_Dispatch"),
    }
    expected_source = {
        0: ("00578555", "Math__TransformVec2ByMatrix4x4"),
        5: ("00578758", "Math__TransformVec2ByMatrixLinear"),
        7: ("005787e8", "Math__NormalizeVec3"),
        9: ("00578643", "Math__TransformVec2ByMatrixPerspective"),
        10: ("00578885", "Math__TransformVec3ByMatrixPerspective"),
        25: ("00577a3e", "Math__BuildEulerRotationMatrix4x4"),
        29: ("005779ae", "CFastVB__BuildAxisAngleQuaternion"),
        35: ("00577eaa", "Math__InterpolateVec4ByRatio"),
        36: ("0057804e", "Math__BlendVec4DualWeights"),
        40: ("0057923a", "CTexture__DispatchMatrixOp00656f94_WithPostOp"),
        43: ("00577fb7", "Math__BezierBlendVec4"),
    }

    for slot, (ptr, name) in expected_runtime.items():
        row = runtime.get(slot)
        require(row is not None, f"missing runtime slot {slot}", failures)
        if row is not None:
            require(row.get("ptr", "").lower() == ptr, f"runtime slot {slot} ptr mismatch: {row}", failures)
            require(row.get("ptr_name") == name, f"runtime slot {slot} name mismatch: {row}", failures)

    for slot, (ptr, name) in expected_source.items():
        row = source.get(slot)
        require(row is not None, f"missing source slot {slot}", failures)
        if row is not None:
            require(row.get("ptr", "").lower() == ptr, f"source slot {slot} ptr mismatch: {row}", failures)
            require(row.get("ptr_name") == name, f"source slot {slot} name mismatch: {row}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-wave660-dry.log": "SUMMARY: updated=0 skipped=17 created=0 would_create=2 body_set=0 would_set_body=2 renamed=0 would_rename=4 signature_updated=15 missing=0 bad=0",
        "apply-wave660-apply.log": "SUMMARY: updated=17 skipped=0 created=2 would_create=0 body_set=2 would_set_body=0 renamed=4 would_rename=0 signature_updated=13 missing=0 bad=0",
        "apply-wave660-final-dry.log": "SUMMARY: updated=0 skipped=17 created=0 would_create=0 body_set=0 would_set_body=0 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "export-post-metadata.log": "targets=17 found=17 missing=0",
        "export-post-tags.log": "ExportFunctionTagsByAddress complete: rows=17 missing=0",
        "export-post-xrefs.log": "Wrote 31 rows to:",
        "export-post-instructions.log": "Wrote 833 instruction rows to:",
        "export-post-decompile.log": "targets=17 dumped=17 missing=0 failed=0",
        "export-dispatch-runtime-table-post.log": "DumpPointerTable complete: rows=71",
        "export-dispatch-source-table-post.log": "DumpPointerTable complete: rows=71",
    }
    for filename, token in expected.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("BAD:" not in text and "MISSING:" not in text, f"bad/missing marker found in {filename}", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require("test:ghidra-math-dispatch-wave660" in package.get("scripts", {}), "package script missing", failures)

    for path in (PUBLIC_NOTE, FUNCTION_INDEX, MATH_DOC, FASTVB_DOC, TEXTURE_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG):
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text, f"{token!r} missing from {path.relative_to(ROOT)}", failures)
        for token in OVERCLAIM_TOKENS:
            require(token not in text, f"overclaim token {token!r} found in {path.relative_to(ROOT)}", failures)

    for path in (LEDGER, ATTEMPT_LOG):
        text = read_text(path)
        require("Wave660 math dispatch continuation" in text, f"Wave660 missing from {path.relative_to(ROOT)}", failures)
        require("math-dispatch-wave660" in text, f"Wave660 tag missing from {path.relative_to(ROOT)}", failures)


def check_state(failures: list[str]) -> None:
    tracking = read_json(TRACKING)
    require(tracking.get("current_focus", "").startswith("Wave660 math dispatch continuation"), "tracking current_focus mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("diffCount") == 0, "backup diffCount mismatch", failures)
    require(backup.get("fileCount") == 19, "backup fileCount mismatch", failures)
    require(backup.get("byteCount") == 163318663, "backup byteCount mismatch", failures)
    require(
        backup.get("backupPath") == "G:\\GhidraBackups\\BEA_20260520-230154_post_wave660_math_dispatch_verified",
        "backup path mismatch",
        failures,
    )

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6098, "queue total mismatch", failures)
    signals = queue.get("qualitySignals", {})
    require(signals.get("commentlessFunctionCount") == 2479, "queue commentless mismatch", failures)
    require(signals.get("undefinedSignatureCount") == 1217, "queue undefined-signature mismatch", failures)
    require(signals.get("paramSignatureCount") == 698, "queue param_N mismatch", failures)
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(head.get("address") == "0x00579184", f"queue head address mismatch: {head}", failures)
    require(head.get("name") == "CFastVB__NormalizeQuaternionCopy", f"queue head name mismatch: {head}", failures)

    ledger_last = read_jsonl(LEDGER)[-1]
    attempt_last = read_jsonl(ATTEMPT_LOG)[-1]
    require(ledger_last.get("task") == "Wave660 math dispatch continuation", "ledger last row mismatch", failures)
    require(attempt_last.get("task") == "Wave660 math dispatch continuation", "attempt task mismatch", failures)
    require(attempt_last.get("attempt_id") == 20315, "attempt id mismatch", failures)
    require(len(read_jsonl(LEDGER)) == 1056, "ledger row count mismatch", failures)
    require(len(read_jsonl(ATTEMPT_LOG)) == 20316, "attempt row count mismatch", failures)
    counters = tracking.get("counters", {})
    require(counters.get("ledger_rows") == 1056, "tracking ledger_rows mismatch", failures)
    require(counters.get("attempt_rows") == 20316, "tracking attempt_rows mismatch", failures)
    require(counters.get("completed") == 1047, "tracking completed mismatch", failures)
    require(counters.get("pending") == 9, "tracking pending mismatch", failures)
    require(tracking.get("next_attempt_id") == 20316, "tracking next_attempt_id mismatch", failures)

    for path in (DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        require("Wave660 math dispatch continuation" in text, f"Wave660 missing from {path.name}", failures)
        require("math-dispatch-wave660" in text, f"Wave660 tag missing from {path.name}", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="return non-zero on validation failure")
    args = parser.parse_args()

    failures: list[str] = []
    try:
        check_metadata(failures)
        check_dispatch_tables(failures)
        check_logs(failures)
        check_docs(failures)
        check_state(failures)
    except Exception as exc:  # noqa: BLE001
        failures.append(f"{type(exc).__name__}: {exc}")

    status = "PASS" if not failures else "FAIL"
    print("Ghidra math dispatch Wave660 probe")
    print(f"Status: {status}")
    print(f"Targets: {len(TARGETS)}")
    print(f"Evidence root: {BASE.relative_to(ROOT)}")
    if failures:
        for failure in failures:
            print(f"- {failure}")
    return 1 if failures and args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
