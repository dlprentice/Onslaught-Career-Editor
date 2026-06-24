#!/usr/bin/env python3
"""Validate Wave658 math/half-float read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave658-math-half-float"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_math_half_float_wave658_2026-05-20.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
MATH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Math.cpp" / "_index.md"
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
BACKUP_SUMMARY = BASE / "backup-summary.json"

COMMON_TAGS = {
    "static-reaudit",
    "math-half-float-wave658",
    "retail-binary-evidence",
    "signature-hardened",
    "comment-hardened",
}

TARGETS = {
    "0x00575986": {
        "name": "Math__IsFloatDiffOutsideTolerance",
        "signature": "int __stdcall Math__IsFloatDiffOutsideTolerance(float lhs, float rhs)",
        "tags": {"math", "float-difference", "tolerance-check", "owner-neutral"},
        "comment_tokens": ("0x005e9314/0x005e9310", "quaternion-copy", "NaN edge behavior"),
        "decompile": "00575986_Math__IsFloatDiffOutsideTolerance.c",
    },
    "0x005759c9": {
        "name": "CFastVB__ConvertFloat32ArrayToFloat16",
        "signature": "void __stdcall CFastVB__ConvertFloat32ArrayToFloat16(void * half_dest, void * float32_source, uint element_count)",
        "tags": {"cfastvb", "half-float", "float32-to-float16", "array-conversion", "dispatch-table-ref"},
        "comment_tokens": ("sign/exponent/mantissa", "rounding and saturation", "dispatch-table ownership"),
        "decompile": "005759c9_CFastVB__ConvertFloat32ArrayToFloat16.c",
    },
    "0x00575a6b": {
        "name": "CFastVB__ConvertFloat16BufferToFloat32_00575a6b",
        "signature": "void * __stdcall CFastVB__ConvertFloat16BufferToFloat32_00575a6b(void * float32_dest, void * half_source, uint element_count)",
        "tags": {"cfastvb", "half-float", "float16-to-float32", "array-conversion", "address-suffixed-helper", "dispatch-table-ref"},
        "comment_tokens": ("zero/subnormal/normal", "returns float32_dest", "IEEE-754 edge-case parity"),
        "decompile": "00575a6b_CFastVB__ConvertFloat16BufferToFloat32_00575a6b.c",
    },
}

DOC_TOKENS = (
    "Wave658 math/half-float hardening",
    "3586",
    "2507",
    "722",
    "0x005771af CFastVB__DispatchIndirect_00656fb4",
    "G:\\GhidraBackups\\BEA_20260520-214232_post_wave658_math_half_float_verified",
)

OVERCLAIM_TOKENS = (
    "runtime math correctness proven",
    "runtime vertex/texture conversion behavior proven",
    "exact IEEE-754 edge-case parity proven",
    "dispatch-table ownership proven",
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
        require("Wave658 math/half-float hardening" in comment, f"missing Wave658 comment at {address}", failures)
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

    require(sum(1 for _ in (BASE / "post-xrefs.tsv").open(encoding="utf-8-sig")) == 18, "post-xrefs.tsv should have 18 lines", failures)
    require(sum(1 for _ in (BASE / "post-instructions.tsv").open(encoding="utf-8-sig")) == 724, "post-instructions.tsv should have 724 lines", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-wave658-dry.log": "SUMMARY: updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=3 missing=0 bad=0",
        "apply-wave658-apply.log": "SUMMARY: updated=3 skipped=0 renamed=0 would_rename=0 signature_updated=3 missing=0 bad=0",
        "apply-wave658-final-dry.log": "SUMMARY: updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "export-post-metadata-relative.log": "targets=3 found=3 missing=0",
        "export-post-tags-relative.log": "ExportFunctionTagsByAddress complete: rows=3 missing=0",
        "export-post-xrefs-relative.log": "Wrote 17 rows to:",
        "export-post-instructions-relative.log": "Wrote 723 instruction rows to:",
        "export-decompile-post-relative.log": "targets=3 dumped=3 missing=0 failed=0",
    }
    for filename, token in expected.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("BAD:" not in text and "MISSING:" not in text, f"bad/missing marker found in {filename}", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require("test:ghidra-math-half-float-wave658" in package.get("scripts", {}), "package script missing", failures)

    for path in (PUBLIC_NOTE, FUNCTION_INDEX, MATH_DOC, FASTVB_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG):
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text, f"{token!r} missing from {path.relative_to(ROOT)}", failures)
        for token in OVERCLAIM_TOKENS:
            require(token not in text, f"overclaim token {token!r} found in {path.relative_to(ROOT)}", failures)

    for path in (LEDGER, ATTEMPT_LOG):
        text = read_text(path)
        require("Wave658 math/half-float hardening" in text, f"Wave658 missing from {path.relative_to(ROOT)}", failures)
        require("math-half-float-wave658" in text, f"Wave658 tag missing from {path.relative_to(ROOT)}", failures)


def check_state(failures: list[str]) -> None:
    tracking = read_json(TRACKING)
    require(tracking.get("next_attempt_id") == 20314, "tracking next_attempt_id mismatch", failures)
    require(tracking.get("current_focus", "").startswith("Wave658 math/half-float hardening"), "tracking current_focus mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("diffCount") == 0, "backup diffCount mismatch", failures)
    require(backup.get("fileCount") == 19, "backup fileCount mismatch", failures)
    require(int(backup.get("byteCount", 0)) == 163253127, "backup byteCount mismatch", failures)
    require(backup.get("backupPath") == "G:\\GhidraBackups\\BEA_20260520-214232_post_wave658_math_half_float_verified", "backup path mismatch", failures)

    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue.get("totalFunctions") == 6093, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 2507, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 1217, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 722, "queue param mismatch", failures)
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(head.get("address") == "0x005771af", "queue head address mismatch", failures)
    require(head.get("name") == "CFastVB__DispatchIndirect_00656fb4", "queue head name mismatch", failures)

    ledger_last = read_jsonl(LEDGER)[-1]
    attempt_last = read_jsonl(ATTEMPT_LOG)[-1]
    require(ledger_last.get("task") == "Wave658 math/half-float hardening", "ledger last row mismatch", failures)
    require(attempt_last.get("attempt_id") == 20313, "attempt id mismatch", failures)
    require(attempt_last.get("task") == "Wave658 math/half-float hardening", "attempt task mismatch", failures)

    for path in (DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        require("Wave658 math/half-float hardening" in text, f"Wave658 missing from {path.name}", failures)
        require("0x005771af CFastVB__DispatchIndirect_00656fb4" in text, f"next queue head missing from {path.name}", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="return non-zero on validation failure")
    args = parser.parse_args()

    failures: list[str] = []
    try:
        check_metadata(failures)
        check_logs(failures)
        check_docs(failures)
        check_state(failures)
    except Exception as exc:  # noqa: BLE001
        failures.append(f"{type(exc).__name__}: {exc}")

    status = "PASS" if not failures else "FAIL"
    print("Ghidra math/half-float Wave658 probe")
    print(f"Status: {status}")
    print(f"Targets: {len(TARGETS)}")
    print(f"Evidence root: {BASE.relative_to(ROOT)}")
    if failures:
        for failure in failures:
            print(f"- {failure}")
    return 1 if failures and args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
