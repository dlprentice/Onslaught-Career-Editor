#!/usr/bin/env python3
"""Validate Wave661 quaternion/matrix read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave661-quaternion-matrix-continuation"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_quaternion_matrix_wave661_2026-05-21.md"
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
    "quaternion-matrix-wave661",
    "retail-binary-evidence",
    "signature-hardened",
    "comment-hardened",
}

TARGETS = {
    "0x00577a0a": {
        "name": "Math__BuildQuaternionFromEulerAngles_Dispatch",
        "signature": "void __stdcall Math__BuildQuaternionFromEulerAngles_Dispatch(void * out_quaternion_xyzw, float angle_x, float angle_y, float angle_z)",
        "tags": {"dispatch-table", "quaternion", "euler", "wave660-correction"},
        "comment_tokens": ("runtime dispatch-table slot 25", "0x00656f94", "corrects the earlier Wave660 matrix wording"),
        "decompile": "00577a0a_Math__BuildQuaternionFromEulerAngles_Dispatch.c",
    },
    "0x00577a38": {
        "name": "Math__BuildQuaternionFromEulerAngles_Dispatch_Thunk",
        "signature": "void __stdcall Math__BuildQuaternionFromEulerAngles_Dispatch_Thunk(void * out_quaternion_xyzw, float angle_x, float angle_y, float angle_z)",
        "tags": {"dispatch-table", "quaternion", "euler", "jump-thunk", "wave660-correction"},
        "comment_tokens": ("pure jump thunk", "runtime dispatch-table slot 25", "corrects the earlier Wave660 matrix wording"),
        "decompile": "00577a38_Math__BuildQuaternionFromEulerAngles_Dispatch_Thunk.c",
    },
    "0x00577a3e": {
        "name": "Math__BuildQuaternionFromEulerAngles",
        "signature": "void __stdcall Math__BuildQuaternionFromEulerAngles(void * out_quaternion_xyzw, float angle_x, float angle_y, float angle_z)",
        "tags": {"source-dispatch-table", "quaternion", "euler", "wave660-correction"},
        "comment_tokens": ("source/default dispatch-table slot 25", "writes four float lanes", "corrects the earlier Wave660 matrix wording"),
        "decompile": "00577a3e_Math__BuildQuaternionFromEulerAngles.c",
    },
    "0x00579184": {
        "name": "CFastVB__NormalizeQuaternionCopy",
        "signature": "void __stdcall CFastVB__NormalizeQuaternionCopy(void * out_quaternion_xyzw, void * input_quaternion_xyzw)",
        "tags": {"source-dispatch-table", "quaternion", "normalize"},
        "comment_tokens": ("source/default dispatch-table slot 8", "measures four quaternion lanes", "near-zero length"),
        "decompile": "00579184_CFastVB__NormalizeQuaternionCopy.c",
    },
    "0x0057923a": {
        "name": "Math__BuildMatrix4x4FromEulerAngles",
        "signature": "void * __stdcall Math__BuildMatrix4x4FromEulerAngles(void * out_matrix4x4, float angle_x, float angle_y, float angle_z)",
        "tags": {"source-dispatch-table", "matrix4x4", "quaternion", "euler", "wave660-correction"},
        "comment_tokens": ("source/default dispatch-table slot 40", "BuildQuaternionFromEulerAngles", "BuildQuaternionRotationMatrix"),
        "decompile": "0057923a_Math__BuildMatrix4x4FromEulerAngles.c",
    },
    "0x00579527": {
        "name": "Math__BuildProjectiveMatrix4x4FromPlane",
        "signature": "void __stdcall Math__BuildProjectiveMatrix4x4FromPlane(void * out_matrix4x4, void * plane_vec4)",
        "tags": {"source-dispatch-table", "matrix4x4", "projective", "plane"},
        "comment_tokens": ("source/default dispatch-table slot 27", "slot-21 vector-normalization", "projective matrix pattern"),
        "decompile": "00579527_Math__BuildProjectiveMatrix4x4FromPlane.c",
    },
    "0x00579601": {
        "name": "Math__BuildMatrix4x4FromQuaternion",
        "signature": "void __stdcall Math__BuildMatrix4x4FromQuaternion(void * out_matrix4x4, void * input_quaternion_xyzw)",
        "tags": {"source-dispatch-table", "matrix4x4", "quaternion"},
        "comment_tokens": ("source/default dispatch-table slot 28", "normalizes/copies quaternion input", "RET 0x8"),
        "decompile": "00579601_Math__BuildMatrix4x4FromQuaternion.c",
    },
}

DOC_TOKENS = (
    "Wave661 quaternion/matrix correction",
    "quaternion-matrix-wave661",
    "0x00577a3e Math__BuildQuaternionFromEulerAngles",
    "0x00579184 CFastVB__NormalizeQuaternionCopy",
    "0x00579b39 CDXTexture__LookupNamedFormatDescriptor",
)

OVERCLAIM_TOKENS = (
    "runtime math correctness proven",
    "exact quaternion convention proven",
    "exact plane equation convention proven",
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
        require("Wave661 quaternion/matrix" in comment, f"missing Wave661 comment at {address}", failures)
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
        25: ("00577a0a", "Math__BuildQuaternionFromEulerAngles_Dispatch"),
        38: ("005775b0", "Math__BuildQuaternionRotationMatrix_Dispatch"),
    }
    expected_source = {
        8: ("00579184", "CFastVB__NormalizeQuaternionCopy"),
        25: ("00577a3e", "Math__BuildQuaternionFromEulerAngles"),
        27: ("00579527", "Math__BuildProjectiveMatrix4x4FromPlane"),
        28: ("00579601", "Math__BuildMatrix4x4FromQuaternion"),
        40: ("0057923a", "Math__BuildMatrix4x4FromEulerAngles"),
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
    expected_exact = {
        "apply-wave661-dry.log": "SUMMARY: updated=0 skipped=7 renamed=0 would_rename=6 signature_updated=7 missing=0 bad=0",
        "apply-wave661-apply.log": "SUMMARY: updated=7 skipped=0 renamed=6 would_rename=0 signature_updated=6 missing=0 bad=0",
        "apply-wave661-final-dry.log": "SUMMARY: updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "export-post-metadata.log": "targets=7 found=7 missing=0",
        "export-post-tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "export-post-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        "export-dispatch-runtime-table-post.log": "DumpPointerTable complete: rows=71",
        "export-dispatch-source-table-post.log": "DumpPointerTable complete: rows=71",
    }
    expected_tokens = {
        "export-post-xrefs.log": ("Wrote ", " rows to:"),
        "export-post-instructions.log": ("Wrote ", " instruction rows to:"),
    }
    for filename, token in expected_exact.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("BAD:" not in text and "MISSING:" not in text, f"bad/missing marker found in {filename}", failures)
    for filename, tokens in expected_tokens.items():
        text = read_text(BASE / filename)
        for token in tokens:
            require(token in text, f"log token missing in {filename}: {token}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("BAD:" not in text and "MISSING:" not in text, f"bad/missing marker found in {filename}", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require("test:ghidra-quaternion-matrix-wave661" in package.get("scripts", {}), "package script missing", failures)

    for path in (PUBLIC_NOTE, FUNCTION_INDEX, MATH_DOC, FASTVB_DOC, TEXTURE_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG):
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text, f"{token!r} missing from {path.relative_to(ROOT)}", failures)
        for token in OVERCLAIM_TOKENS:
            require(token not in text, f"overclaim token {token!r} found in {path.relative_to(ROOT)}", failures)

    for path in (LEDGER, ATTEMPT_LOG):
        text = read_text(path)
        require("Wave661 quaternion/matrix correction" in text, f"Wave661 missing from {path.relative_to(ROOT)}", failures)
        require("quaternion-matrix-wave661" in text, f"Wave661 tag missing from {path.relative_to(ROOT)}", failures)


def check_state(failures: list[str]) -> None:
    tracking = read_json(TRACKING)
    require(tracking.get("current_focus", "").startswith("Wave661 quaternion/matrix correction"), "tracking current_focus mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("diffCount") == 0, "backup diffCount mismatch", failures)
    require(backup.get("fileCount") == 19, "backup fileCount mismatch", failures)
    require(backup.get("byteCount", 0) > 160_000_000, "backup byteCount too small", failures)
    require("post_wave661_quaternion_matrix_verified" in backup.get("backupPath", ""), "backup path mismatch", failures)

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6098, "queue total mismatch", failures)
    signals = queue.get("qualitySignals", {})
    require(signals.get("commentlessFunctionCount") == 2475, "queue commentless mismatch", failures)
    require(signals.get("undefinedSignatureCount") == 1217, "queue undefined-signature mismatch", failures)
    require(signals.get("paramSignatureCount") == 694, "queue param_N mismatch", failures)
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(head.get("address") == "0x00579b39", f"queue head address mismatch: {head}", failures)
    require(head.get("name") == "CDXTexture__LookupNamedFormatDescriptor", f"queue head name mismatch: {head}", failures)

    ledger_last = read_jsonl(LEDGER)[-1]
    attempt_last = read_jsonl(ATTEMPT_LOG)[-1]
    require(ledger_last.get("task") == "Wave661 quaternion/matrix correction", "ledger last row mismatch", failures)
    require(attempt_last.get("task") == "Wave661 quaternion/matrix correction", "attempt task mismatch", failures)
    require(attempt_last.get("attempt_id") == 20316, "attempt id mismatch", failures)
    require(len(read_jsonl(LEDGER)) == 1057, "ledger row count mismatch", failures)
    require(len(read_jsonl(ATTEMPT_LOG)) == 20317, "attempt row count mismatch", failures)
    counters = tracking.get("counters", {})
    require(counters.get("ledger_rows") == 1057, "tracking ledger_rows mismatch", failures)
    require(counters.get("attempt_rows") == 20317, "tracking attempt_rows mismatch", failures)
    require(counters.get("completed") == 1048, "tracking completed mismatch", failures)
    require(counters.get("pending") == 9, "tracking pending mismatch", failures)
    require(tracking.get("next_attempt_id") == 20317, "tracking next_attempt_id mismatch", failures)

    for path in (DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        require("Wave661 quaternion/matrix correction" in text, f"Wave661 missing from {path.name}", failures)
        require("quaternion-matrix-wave661" in text, f"Wave661 tag missing from {path.name}", failures)


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
    print("Ghidra quaternion/matrix Wave661 probe")
    print(f"Status: {status}")
    print(f"Targets: {len(TARGETS)}")
    print(f"Evidence root: {BASE.relative_to(ROOT)}")
    if failures:
        for failure in failures:
            print(f"- {failure}")
    return 1 if failures and args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
