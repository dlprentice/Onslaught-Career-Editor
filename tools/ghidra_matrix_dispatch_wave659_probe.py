#!/usr/bin/env python3
"""Validate Wave659 matrix dispatch read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave659-matrix-dispatch"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_matrix_dispatch_wave659_2026-05-21.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
MATH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Math.cpp" / "_index.md"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
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
    "matrix-dispatch-wave659",
    "retail-binary-evidence",
    "signature-hardened",
    "comment-hardened",
}

TARGETS = {
    "0x005771af": {
        "name": "Math__BuildScaleMatrix4x4_Dispatch",
        "signature": "void __stdcall Math__BuildScaleMatrix4x4_Dispatch(void * out_matrix4x4, float scale_x, float scale_y, float scale_z)",
        "tags": {"dispatch-table", "matrix4x4", "scale-matrix"},
        "comment_tokens": ("runtime dispatch-table slot 33", "0x00656fb4", "0x005771dd scale-matrix builder"),
        "decompile": "005771af_Math__BuildScaleMatrix4x4_Dispatch.c",
    },
    "0x005771dd": {
        "name": "Math__BuildScaleMatrix4x4",
        "signature": "void __stdcall Math__BuildScaleMatrix4x4(void * out_matrix4x4, float scale_x, float scale_y, float scale_z)",
        "tags": {"source-dispatch-table", "boundary-recovered", "matrix4x4", "scale-matrix"},
        "comment_tokens": ("source/default dispatch-table slot 33", "RET 0x10 at 0x00577236", "bottom-right 1.0"),
        "decompile": "005771dd_Math__BuildScaleMatrix4x4.c",
    },
    "0x00577239": {
        "name": "Math__BuildTranslationMatrix4x4_Dispatch",
        "signature": "void __stdcall Math__BuildTranslationMatrix4x4_Dispatch(void * out_matrix4x4, float translate_x, float translate_y, float translate_z)",
        "tags": {"dispatch-table", "matrix4x4", "translation-matrix"},
        "comment_tokens": ("runtime dispatch-table slot 26", "0x00656f98", "0x0057726d translation-matrix builder"),
        "decompile": "00577239_Math__BuildTranslationMatrix4x4_Dispatch.c",
    },
    "0x00577267": {
        "name": "Math__BuildTranslationMatrix4x4_Dispatch_Thunk",
        "signature": "void __stdcall Math__BuildTranslationMatrix4x4_Dispatch_Thunk(void * out_matrix4x4, float translate_x, float translate_y, float translate_z)",
        "tags": {"dispatch-table", "matrix4x4", "translation-matrix", "jump-thunk"},
        "comment_tokens": ("pure jump thunk", "runtime dispatch-table slot 26", "0x00656f98"),
        "decompile": "00577267_Math__BuildTranslationMatrix4x4_Dispatch_Thunk.c",
    },
    "0x0057726d": {
        "name": "Math__BuildTranslationMatrix4x4",
        "signature": "void __stdcall Math__BuildTranslationMatrix4x4(void * out_matrix4x4, float translate_x, float translate_y, float translate_z)",
        "tags": {"source-dispatch-table", "boundary-recovered", "matrix4x4", "translation-matrix"},
        "comment_tokens": ("source/default dispatch-table slot 26", "offsets 0x30/0x34/0x38", "RET 0x10 at 0x005772c6"),
        "decompile": "0057726d_Math__BuildTranslationMatrix4x4.c",
    },
    "0x005772c9": {
        "name": "Math__BuildRotationMatrixX_Dispatch",
        "signature": "void __stdcall Math__BuildRotationMatrixX_Dispatch(void * out_matrix4x4, float angle_radians)",
        "tags": {"dispatch-table", "matrix4x4", "rotation-matrix", "x-axis"},
        "comment_tokens": ("runtime dispatch-table slot 30", "0x00656fa8", "0x005772e5"),
        "decompile": "005772c9_Math__BuildRotationMatrixX_Dispatch.c",
    },
    "0x005772e5": {
        "name": "Math__BuildRotationMatrixX",
        "signature": "void __stdcall Math__BuildRotationMatrixX(void * out_matrix4x4, float angle_radians)",
        "tags": {"source-dispatch-table", "matrix4x4", "rotation-matrix", "x-axis"},
        "comment_tokens": ("source/default dispatch-table slot 30", "FSINCOS", "X-axis rotation matrix"),
        "decompile": "005772e5_Math__BuildRotationMatrixX.c",
    },
    "0x0057735f": {
        "name": "Math__BuildRotationMatrixY_Dispatch",
        "signature": "void __stdcall Math__BuildRotationMatrixY_Dispatch(void * out_matrix4x4, float angle_radians)",
        "tags": {"dispatch-table", "matrix4x4", "rotation-matrix", "y-axis"},
        "comment_tokens": ("runtime dispatch-table slot 31", "0x00656fac", "0x0057737b"),
        "decompile": "0057735f_Math__BuildRotationMatrixY_Dispatch.c",
    },
    "0x0057737b": {
        "name": "Math__BuildRotationMatrixY",
        "signature": "void __stdcall Math__BuildRotationMatrixY(void * out_matrix4x4, float angle_radians)",
        "tags": {"source-dispatch-table", "matrix4x4", "rotation-matrix", "y-axis"},
        "comment_tokens": ("source/default dispatch-table slot 31", "FSINCOS", "Y-axis rotation matrix"),
        "decompile": "0057737b_Math__BuildRotationMatrixY.c",
    },
    "0x005773f6": {
        "name": "Math__BuildRotationMatrixZ_Dispatch",
        "signature": "void __stdcall Math__BuildRotationMatrixZ_Dispatch(void * out_matrix4x4, float angle_radians)",
        "tags": {"dispatch-table", "matrix4x4", "rotation-matrix", "z-axis"},
        "comment_tokens": ("runtime dispatch-table slot 32", "0x00656fb0", "0x00577412"),
        "decompile": "005773f6_Math__BuildRotationMatrixZ_Dispatch.c",
    },
    "0x00577412": {
        "name": "Math__BuildRotationMatrixZ",
        "signature": "void __stdcall Math__BuildRotationMatrixZ(void * out_matrix4x4, float angle_radians)",
        "tags": {"source-dispatch-table", "matrix4x4", "rotation-matrix", "z-axis"},
        "comment_tokens": ("source/default dispatch-table slot 32", "FSINCOS", "Z-axis rotation matrix"),
        "decompile": "00577412_Math__BuildRotationMatrixZ.c",
    },
    "0x0057748e": {
        "name": "Math__BuildAxisAngleRotationMatrix_Dispatch",
        "signature": "void __stdcall Math__BuildAxisAngleRotationMatrix_Dispatch(void * out_matrix4x4, void * axis_vec3, float angle_radians)",
        "tags": {"dispatch-table", "matrix4x4", "rotation-matrix", "axis-angle"},
        "comment_tokens": ("runtime dispatch-table slot 42", "0x00656fd8", "0x005774ae"),
        "decompile": "0057748e_Math__BuildAxisAngleRotationMatrix_Dispatch.c",
    },
    "0x005774ae": {
        "name": "Math__BuildAxisAngleRotationMatrix",
        "signature": "void __stdcall Math__BuildAxisAngleRotationMatrix(void * out_matrix4x4, void * axis_vec3, float angle_radians)",
        "tags": {"source-dispatch-table", "matrix4x4", "rotation-matrix", "axis-angle"},
        "comment_tokens": ("source/default dispatch-table slot 42", "0x006570f8", "axis-angle rotation matrix"),
        "decompile": "005774ae_Math__BuildAxisAngleRotationMatrix.c",
    },
    "0x005775b0": {
        "name": "Math__BuildQuaternionRotationMatrix_Dispatch",
        "signature": "void __stdcall Math__BuildQuaternionRotationMatrix_Dispatch(void * out_matrix4x4, void * quaternion_xyzw)",
        "tags": {"dispatch-table", "matrix4x4", "rotation-matrix", "quaternion"},
        "comment_tokens": ("runtime dispatch-table slot 38", "0x00656fc8", "0x005775c3 builder"),
        "decompile": "005775b0_Math__BuildQuaternionRotationMatrix_Dispatch.c",
    },
    "0x005775bd": {
        "name": "Math__BuildQuaternionRotationMatrix_Dispatch_Thunk",
        "signature": "void __stdcall Math__BuildQuaternionRotationMatrix_Dispatch_Thunk(void * out_matrix4x4, void * quaternion_xyzw)",
        "tags": {"dispatch-table", "matrix4x4", "rotation-matrix", "quaternion", "jump-thunk"},
        "comment_tokens": ("pure jump thunk", "runtime dispatch-table slot 38", "0x00656fc8"),
        "decompile": "005775bd_Math__BuildQuaternionRotationMatrix_Dispatch_Thunk.c",
    },
    "0x005775c3": {
        "name": "Math__BuildQuaternionRotationMatrix",
        "signature": "void __stdcall Math__BuildQuaternionRotationMatrix(void * out_matrix4x4, void * quaternion_xyzw)",
        "tags": {"source-dispatch-table", "boundary-recovered", "matrix4x4", "rotation-matrix", "quaternion"},
        "comment_tokens": ("source/default dispatch-table slot 38", "constant 0x005e9324", "RET 0x8 at 0x005776a2"),
        "decompile": "005775c3_Math__BuildQuaternionRotationMatrix.c",
    },
}

DOC_TOKENS = (
    "Wave659 matrix dispatch hardening",
    "3602",
    "2494",
    "711",
    "3552/6096 = 58.27%",
    "0x005776a5 CTexture__DispatchPtr00656fd0_WithInit",
    "G:\\GhidraBackups\\BEA_20260521-221700_post_wave659_matrix_dispatch_verified",
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
        require("Wave659 matrix dispatch" in comment, f"missing Wave659 comment at {address}", failures)
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

    require(sum(1 for _ in (BASE / "post-xrefs.tsv").open(encoding="utf-8-sig")) == 29, "post-xrefs.tsv should have 29 lines", failures)
    require(sum(1 for _ in (BASE / "post-instructions.tsv").open(encoding="utf-8-sig")) == 2417, "post-instructions.tsv should have 2417 lines", failures)


def check_dispatch_tables(failures: list[str]) -> None:
    runtime = table_by_slot(BASE / "dispatch-runtime-table-post.tsv")
    source = table_by_slot(BASE / "dispatch-source-table-post.tsv")

    expected_runtime = {
        26: ("00577239", "Math__BuildTranslationMatrix4x4_Dispatch"),
        30: ("005772c9", "Math__BuildRotationMatrixX_Dispatch"),
        31: ("0057735f", "Math__BuildRotationMatrixY_Dispatch"),
        32: ("005773f6", "Math__BuildRotationMatrixZ_Dispatch"),
        33: ("005771af", "Math__BuildScaleMatrix4x4_Dispatch"),
        38: ("005775b0", "Math__BuildQuaternionRotationMatrix_Dispatch"),
        42: ("0057748e", "Math__BuildAxisAngleRotationMatrix_Dispatch"),
    }
    expected_source = {
        26: ("0057726d", "Math__BuildTranslationMatrix4x4"),
        30: ("005772e5", "Math__BuildRotationMatrixX"),
        31: ("0057737b", "Math__BuildRotationMatrixY"),
        32: ("00577412", "Math__BuildRotationMatrixZ"),
        33: ("005771dd", "Math__BuildScaleMatrix4x4"),
        38: ("005775c3", "Math__BuildQuaternionRotationMatrix"),
        42: ("005774ae", "Math__BuildAxisAngleRotationMatrix"),
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
        "apply-wave659-dry.log": "SUMMARY: updated=0 skipped=16 created=0 would_create=3 body_set=0 would_set_body=3 renamed=0 would_rename=5 signature_updated=13 missing=0 bad=0",
        "apply-wave659-apply.log": "SUMMARY: updated=16 skipped=0 created=3 would_create=0 body_set=3 would_set_body=0 renamed=5 would_rename=0 signature_updated=11 missing=0 bad=0",
        "apply-wave659-final-dry.log": "SUMMARY: updated=0 skipped=16 created=0 would_create=0 body_set=0 would_set_body=0 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "export-post-metadata.log": "targets=16 found=16 missing=0",
        "export-post-tags.log": "ExportFunctionTagsByAddress complete: rows=16 missing=0",
        "export-post-xrefs.log": "Wrote 28 rows to:",
        "export-post-instructions.log": "Wrote 2416 instruction rows to:",
        "export-post-decompile.log": "targets=16 dumped=16 missing=0 failed=0",
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
    require("test:ghidra-matrix-dispatch-wave659" in package.get("scripts", {}), "package script missing", failures)

    for path in (PUBLIC_NOTE, FUNCTION_INDEX, MATH_DOC, FASTVB_DOC, DXTEXTURE_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG):
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text, f"{token!r} missing from {path.relative_to(ROOT)}", failures)
        for token in OVERCLAIM_TOKENS:
            require(token not in text, f"overclaim token {token!r} found in {path.relative_to(ROOT)}", failures)

    for path in (LEDGER, ATTEMPT_LOG):
        text = read_text(path)
        require("Wave659 matrix dispatch hardening" in text, f"Wave659 missing from {path.relative_to(ROOT)}", failures)
        require("matrix-dispatch-wave659" in text, f"Wave659 tag missing from {path.relative_to(ROOT)}", failures)


def check_state(failures: list[str]) -> None:
    tracking = read_json(TRACKING)
    require(tracking.get("next_attempt_id") == 20315, "tracking next_attempt_id mismatch", failures)
    require(tracking.get("counters", {}).get("ledger_rows") == 1055, "tracking ledger_rows mismatch", failures)
    require(tracking.get("counters", {}).get("attempt_rows") == 20315, "tracking attempt_rows mismatch", failures)
    require(tracking.get("current_focus", "").startswith("Wave659 matrix dispatch hardening"), "tracking current_focus mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("diffCount") == 0, "backup diffCount mismatch", failures)
    require(backup.get("fileCount") == 19, "backup fileCount mismatch", failures)
    require(int(backup.get("byteCount", 0)) == 163285895, "backup byteCount mismatch", failures)
    require(backup.get("backupPath") == "G:\\GhidraBackups\\BEA_20260521-221700_post_wave659_matrix_dispatch_verified", "backup path mismatch", failures)

    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue.get("totalFunctions") == 6096, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 2494, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 1217, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 711, "queue param mismatch", failures)
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(head.get("address") == "0x005776a5", "queue head address mismatch", failures)
    require(head.get("name") == "CTexture__DispatchPtr00656fd0_WithInit", "queue head name mismatch", failures)

    ledger_last = read_jsonl(LEDGER)[-1]
    attempt_last = read_jsonl(ATTEMPT_LOG)[-1]
    require(ledger_last.get("task") == "Wave659 matrix dispatch hardening", "ledger last row mismatch", failures)
    require(attempt_last.get("attempt_id") == 20314, "attempt id mismatch", failures)
    require(attempt_last.get("task") == "Wave659 matrix dispatch hardening", "attempt task mismatch", failures)

    for path in (DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        require("Wave659 matrix dispatch hardening" in text, f"Wave659 missing from {path.name}", failures)
        require("0x005776a5 CTexture__DispatchPtr00656fd0_WithInit" in text, f"next queue head missing from {path.name}", failures)


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
    print("Ghidra matrix dispatch Wave659 probe")
    print(f"Status: {status}")
    print(f"Targets: {len(TARGETS)}")
    print(f"Evidence root: {BASE.relative_to(ROOT)}")
    if failures:
        for failure in failures:
            print(f"- {failure}")
    return 1 if failures and args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
