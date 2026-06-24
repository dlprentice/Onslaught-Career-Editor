#!/usr/bin/env python3
"""Validate Wave897 CFastVB SIMD-transform read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave897-cfastvb-simd-transform-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cfastvb_simd_transform_tail_wave897_2026-05-26.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260526-074111_post_wave897_cfastvb_simd_transform_tail_verified"
COMMON_TAGS = {
    "static-reaudit",
    "cfastvb-simd-transform-tail-wave897",
    "wave897-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-verified",
    "important-cfastvb-math-infrastructure",
    "raw-commentless-tail",
    "simd-transform-tail",
}
TARGETS = {
    "0x005a09f8": {
        "name": "CFastVB__ConvertHalfToFloat8_SIMDKernel",
        "signature": "void CFastVB__ConvertHalfToFloat8_SIMDKernel(void)",
        "tokens": ("Wave897 static read-back", "0x005a0b53", "MULPS", "XMM/MMX ABI"),
        "xrefs": {"0x005a0b53"},
        "extra_tags": {"half-float-conversion", "hidden-register-abi", "sse-kernel"},
    },
    "0x005a1c55": {
        "name": "CFastVB__DispatchOp_TransformVec4Batch_Alt_005a1c55",
        "signature": "int CFastVB__DispatchOp_TransformVec4Batch_Alt_005a1c55(void)",
        "tokens": ("Wave897 static read-back", "0x00598365", "CFastVB__BroadcastMatrix4x4ToSIMDLanes", "CFastVB__DispatchOp_TransformVec4ByMatrix4_005a3200"),
        "xrefs": {"0x00598365"},
        "extra_tags": {"dispatch-table-data-xref", "vec4-transform-batch", "scalar-tail-fallback"},
    },
    "0x005a1e5b": {
        "name": "CFastVB__DispatchOp_TransformVec4BatchW_Alt_005a1e5b",
        "signature": "int CFastVB__DispatchOp_TransformVec4BatchW_Alt_005a1e5b(void)",
        "tokens": ("Wave897 static read-back", "0x00598347", "CFastVB__DispatchIndirect_00656f30", "RET 0x18"),
        "xrefs": {"0x00598347"},
        "extra_tags": {"dispatch-table-data-xref", "vec4w-transform-batch", "dispatch-tail-fallback"},
    },
    "0x005a1fe9": {
        "name": "CFastVB__DispatchOp_TransformProjectVec4Batch_Alt_005a1fe9",
        "signature": "int CFastVB__DispatchOp_TransformProjectVec4Batch_Alt_005a1fe9(void)",
        "tokens": ("Wave897 static read-back", "0x00598351", "RCPPS", "CFastVB__DispatchIndirect_00656f54"),
        "xrefs": {"0x00598351"},
        "extra_tags": {"dispatch-table-data-xref", "projected-vec4-batch", "rcpps-projection"},
    },
    "0x005a214f": {
        "name": "CFastVB__DispatchOp_TransformVec4Batch_NoOffset_Alt_005a214f",
        "signature": "int CFastVB__DispatchOp_TransformVec4Batch_NoOffset_Alt_005a214f(void)",
        "tokens": ("Wave897 static read-back", "0x0059835b", "CFastVB__DispatchIndirect_00656f44", "RET 0x18"),
        "xrefs": {"0x0059835b"},
        "extra_tags": {"dispatch-table-data-xref", "no-offset-vec4-batch", "dispatch-tail-fallback"},
    },
    "0x005a225f": {
        "name": "CFastVB__DispatchOp_TransformVec4Batch_Perspective_Alt_005a225f",
        "signature": "int CFastVB__DispatchOp_TransformVec4Batch_Perspective_Alt_005a225f(void)",
        "tokens": ("Wave897 static read-back", "0x0059823e", "0x00598383", "0x00598389", "CFastVB__DispatchOp_TransformVec2ByMatrix4"),
        "xrefs": {"0x0059823e", "0x00598383", "0x00598389"},
        "extra_tags": {"dispatch-table-data-xref", "perspective-vec4-batch", "scalar-tail-fallback"},
    },
    "0x005a249d": {
        "name": "CFastVB__DispatchOp_TransformVec3WBatch_Alt_005a249d",
        "signature": "int CFastVB__DispatchOp_TransformVec3WBatch_Alt_005a249d(void)",
        "tokens": ("Wave897 static read-back", "0x00598379", "CFastVB__DispatchOp_TransformVec3ByMatrix4_005a16b1", "RET 0x18"),
        "xrefs": {"0x00598379"},
        "extra_tags": {"dispatch-table-data-xref", "vec3w-transform-batch", "scalar-tail-fallback"},
    },
    "0x005a266d": {
        "name": "CFastVB__TransformProjectVec3ByMatrix4_Batch4",
        "signature": "int CFastVB__TransformProjectVec3ByMatrix4_Batch4(void)",
        "tokens": ("Wave897 static read-back", "0x0059836f", "RCPPS", "CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a1786"),
        "xrefs": {"0x0059836f"},
        "extra_tags": {"dispatch-table-data-xref", "projected-vec3-batch4", "rcpps-projection"},
    },
    "0x005a289e": {
        "name": "CFastVB__ConvertHalfToFloat8_CheckSpecialCasesSIMD",
        "signature": "void CFastVB__ConvertHalfToFloat8_CheckSpecialCasesSIMD(void)",
        "tokens": ("Wave897 static read-back", "0x005a29c0", "0x0065e750", "half-float lanes"),
        "xrefs": {"0x005a29c0"},
        "extra_tags": {"half-float-conversion", "hidden-register-abi", "special-case-screen"},
    },
}
CORE_ANCHORS = (
    "Wave897 CFastVB SIMD transform tail",
    "cfastvb-simd-transform-tail-wave897",
    "0x005a09f8 CFastVB__ConvertHalfToFloat8_SIMDKernel",
    "0x005a1c55 CFastVB__DispatchOp_TransformVec4Batch_Alt_005a1c55",
    "0x005a266d CFastVB__TransformProjectVec3ByMatrix4_Batch4",
    "0x005a289e CFastVB__ConvertHalfToFloat8_CheckSpecialCasesSIMD",
    "0x005a9f44 CFastVB__DispatchOp_ComposeTransformAndProjectVec3_005a9f44",
    "6097/6113 = 99.74%",
    BACKUP_PATH,
)
OVERCLAIM_TOKENS = (
    "runtime math correctness proven",
    "runtime renderer behavior proven",
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


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict_clean


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 9,
        "pre-tags.tsv": 9,
        "pre-xrefs.tsv": 11,
        "pre-instructions.tsv": 1077,
        "pre-decompile/index.tsv": 9,
        "pre-context-metadata.tsv": 10,
        "post-metadata.tsv": 9,
        "post-tags.tsv": 9,
        "post-xrefs.tsv": 11,
        "post-instructions.tsv": 1077,
        "post-decompile/index.tsv": 9,
        "post-context-metadata.tsv": 10,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    xrefs_by_target: dict[str, set[str]] = {}
    for row in read_tsv(BASE / "post-xrefs.tsv"):
        xrefs_by_target.setdefault(normalize_address(row["target_addr"]), set()).add(normalize_address(row["from_addr"]))
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, expected in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == expected["name"], f"name mismatch at {address}", failures)
            require(row.get("signature") == expected["signature"], f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in expected["tokens"]:
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            needed = COMMON_TAGS | expected["extra_tags"]
            require(needed.issubset(actual_tags), f"tags missing at {address}: {needed - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        require(expected["xrefs"].issubset(xrefs_by_target.get(address, set())), f"xref anchors missing at {address}", failures)
        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row at {address}", failures)
        if dec is not None:
            require(dec.get("signature") == expected["signature"], f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=9 renamed=0 would_rename=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=9 skipped=0 renamed=0 would_rename=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=9 renamed=0 would_rename=0 missing=0 bad=0",
        "post-metadata.log": "targets=9 found=9 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=9 missing=0",
        "post-xrefs.log": "Wrote 11 rows",
        "post-instructions.log": "Wrote 1077 function-body instruction rows",
        "post-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
        "post-context-metadata.log": "targets=10 found=10 missing=0",
        "quality-refresh.log": "total_functions=6113 commented_functions=6097",
        "queue-probe.log": "Commentless functions: 16",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave897.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave897_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6113, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 16, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6113, "quality TSV row count mismatch", failures)
    require(commented == 6097, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6097, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x005a9f44", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CFastVB__DispatchOp_ComposeTransformAndProjectVec3_005a9f44", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 173214599, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    for path in (PUBLIC_NOTE, FUNCTION_INDEX, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG, FASTVB_DOC, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-cfastvb-simd-transform-tail-wave897") == r"py -3 tools\ghidra_cfastvb_simd_transform_tail_wave897_probe.py --check",
        "missing package script",
        failures,
    )
    require(any(row.get("task") == "Wave897 CFastVB SIMD transform tail" for row in read_jsonl(LEDGER)), "missing Wave897 ledger row", failures)
    require(any(row.get("task") == "Wave897 CFastVB SIMD transform tail" and row.get("attempt_id") == 20552 for row in read_jsonl(ATTEMPT_LOG)), "missing Wave897 attempt row", failures)


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
        print("Wave897 CFastVB SIMD-transform probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave897 CFastVB SIMD-transform probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
