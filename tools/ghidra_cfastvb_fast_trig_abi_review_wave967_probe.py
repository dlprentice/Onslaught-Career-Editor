#!/usr/bin/env python3
"""Validate Wave967 CFastVB fast-trig ABI review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave967-cfastvb-fast-trig-abi-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_cfastvb_fast_trig_abi_review_wave967_2026-05-28.md"
PACKAGE_JSON = ROOT / "package.json"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUALITY_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260528-160046_post_wave967_cfastvb_fast_trig_abi_review_verified"
TAG = "cfastvb-fast-trig-abi-review-wave967"

EXPECTED_METADATA = {
    "0x005a4c67": (
        "CFastVB__DispatchOp_ComposeQuaternionFromFastTrigPairs_005a4c67",
        "void __stdcall CFastVB__DispatchOp_ComposeQuaternionFromFastTrigPairs_005a4c67(void * out_quaternion_lanes, int packed_lane_arg2, int packed_lane_arg3, int packed_lane_arg4)",
        ("slot +0x64", "0x00598537", "RET 0x10", "CFastVB__FastTrigPairApprox_Scalar", "quaternion-like output lanes"),
    ),
    "0x005a60ef": (
        "CFastVB__DispatchOp_BuildRotationMatrixX_FastTrig_005a60ef",
        "void __stdcall CFastVB__DispatchOp_BuildRotationMatrixX_FastTrig_005a60ef(void * out_matrix4x4, float angle_radians)",
        ("slot +0x78", "0x0059855a", "RET 0x8", "0x40-byte X-axis rotation-matrix-style output block"),
    ),
    "0x005a6152": (
        "CFastVB__DispatchOp_BuildRotationMatrixY_FastTrig_005a6152",
        "void __stdcall CFastVB__DispatchOp_BuildRotationMatrixY_FastTrig_005a6152(void * out_matrix4x4, float angle_radians)",
        ("slot +0x7c", "0x00598561", "RET 0x8", "0x40-byte Y-axis rotation-matrix-style output block"),
    ),
    "0x005a61b0": (
        "CFastVB__DispatchOp_BuildRotationMatrixZ_FastTrig_005a61b0",
        "void __stdcall CFastVB__DispatchOp_BuildRotationMatrixZ_FastTrig_005a61b0(void * out_matrix4x4, float angle_radians)",
        ("slot +0x80", "0x00598568", "RET 0x8", "0x40-byte Z-axis rotation-matrix-style output block"),
    ),
}

EXPECTED_XREFS = {
    "0x005a4c67": "0x00598537",
    "0x005a60ef": "0x0059855a",
    "0x005a6152": "0x00598561",
    "0x005a61b0": "0x00598568",
}

BODY_EVIDENCE = {
    "0x005a4c67": {
        "terminal": ("0x005a4d29", "RET", "0x10"),
        "calls": ("0x005a4c89", "0x005a4c9a", "0x005a4ca9"),
        "forbidden": ("0x005a4d2c",),
    },
    "0x005a60ef": {
        "terminal": ("0x005a614f", "RET", "0x8"),
        "calls": ("0x005a60f8",),
        "forbidden": ("0x005a6152",),
    },
    "0x005a6152": {
        "terminal": ("0x005a61ad", "RET", "0x8"),
        "calls": ("0x005a615b",),
        "forbidden": ("0x005a61b0",),
    },
    "0x005a61b0": {
        "terminal": ("0x005a6206", "RET", "0x8"),
        "calls": ("0x005a61b9",),
        "forbidden": ("0x005a6209",),
    },
}

COMMON_TAGS = {
    "static-reaudit",
    TAG,
    "wave967-readback-verified",
    "retail-binary-evidence",
    "function-boundary-recovered",
    "signature-hardened",
    "comment-hardened",
    "dispatch-table-target",
    "packed-mmx",
    "fast-trig",
}

CORE_TOKENS = (
    "Wave967",
    TAG,
    "0x005a4c67 CFastVB__DispatchOp_ComposeQuaternionFromFastTrigPairs_005a4c67",
    "0x005a60ef CFastVB__DispatchOp_BuildRotationMatrixX_FastTrig_005a60ef",
    "0x005a6152 CFastVB__DispatchOp_BuildRotationMatrixY_FastTrig_005a6152",
    "0x005a61b0 CFastVB__DispatchOp_BuildRotationMatrixZ_FastTrig_005a61b0",
    "0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags",
    "0x005b8ca0 CFastVB__FastTrigPairApprox_Scalar",
    "344/1408 = 24.43%",
    "348/1412 = 24.65%",
    "6156/6156 = 100.00%",
    BACKUP_PATH,
    "function-boundary recovery",
)

OVERCLAIMS = (
    "runtime math behavior proven",
    "runtime render behavior proven",
    "runtime cpu dispatch behavior proven",
    "layout proven",
    "source identity proven",
    "patching proven",
    "rebuild parity proven",
)


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


def norm(address: str) -> str:
    value = (address or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    if value in {"", "<none>", "none"}:
        return value
    return "0x" + value.zfill(8)


def contains_token(text: str, token: str) -> bool:
    stripped = text.replace("`", "")
    return token in text or token in stripped or token.replace("\\", "\\\\") in text or token.replace("\\", "\\\\") in stripped


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


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


def check_counts(failures: list[str]) -> None:
    expected = {
        "pre-metadata.tsv": 13,
        "pre-tags.tsv": 13,
        "pre-xrefs.tsv": 28,
        "pre-body-instructions.tsv": 1413,
        "pre-xref-site-instructions.tsv": 930,
        "pre-decompile/index.tsv": 13,
        "pre-constant-xrefs.tsv": 32,
        "pre-orphan-metadata.tsv": 4,
        "pre-orphan-xrefs.tsv": 4,
        "pre-orphan-instructions.tsv": 356,
        "pre-dispatch-context-body.tsv": 89,
        "pre-dispatch-context-around.tsv": 125,
        "pre-dispatch-context-decompile/index.tsv": 5,
        "post-created-metadata.tsv": 4,
        "post-created-tags.tsv": 4,
        "post-created-xrefs.tsv": 4,
        "post-created-body-instructions.tsv": 131,
        "post-created-decompile/index.tsv": 4,
    }
    for relative, count in expected.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == count, f"{relative} row count mismatch: {actual} != {count}", failures)


def check_artifacts(failures: list[str]) -> None:
    pre_missing = {norm(row["address"]): row for row in read_tsv(BASE / "pre-orphan-metadata.tsv")}
    for address in EXPECTED_METADATA:
        row = pre_missing.get(address)
        require(row is not None, f"missing pre-orphan metadata row for {address}", failures)
        if row:
            require(row.get("status") == "MISSING", f"pre-orphan status mismatch at {address}", failures)

    post = {norm(row["address"]): row for row in read_tsv(BASE / "post-created-metadata.tsv")}
    tags = {norm(row["address"]): row for row in read_tsv(BASE / "post-created-tags.tsv")}
    xrefs = {norm(row["target_addr"]): row for row in read_tsv(BASE / "post-created-xrefs.tsv")}
    body = read_tsv(BASE / "post-created-body-instructions.tsv")
    decompile = {norm(row["address"]): row for row in read_tsv(BASE / "post-created-decompile" / "index.tsv")}

    for address, (name, signature, tokens) in EXPECTED_METADATA.items():
        row = post.get(address)
        require(row is not None, f"missing post metadata for {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch at {address}: {row.get('name')}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in tokens:
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tag gap at {address}: {COMMON_TAGS - actual_tags}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index row for {address}", failures)
        if dec:
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)

        xref = xrefs.get(address)
        require(xref is not None, f"missing DATA xref for {address}", failures)
        if xref:
            require(norm(xref.get("from_addr", "")) == EXPECTED_XREFS[address], f"xref source mismatch at {address}", failures)
            require(xref.get("ref_type") == "DATA", f"xref type mismatch at {address}", failures)

    by_function = {}
    for row in body:
        by_function.setdefault(norm(row.get("function_entry", "")), []).append(row)

    for address, evidence in BODY_EVIDENCE.items():
        rows = by_function.get(address, [])
        require(rows, f"missing body rows for {address}", failures)
        terminal_addr, terminal_mnemonic, terminal_operand = evidence["terminal"]
        require(
            any(
                norm(row.get("instruction_addr", "")) == terminal_addr
                and row.get("mnemonic") == terminal_mnemonic
                and terminal_operand in row.get("operands", "")
                for row in rows
            ),
            f"missing terminal evidence for {address}",
            failures,
        )
        for call_addr in evidence["calls"]:
            require(
                any(
                    norm(row.get("instruction_addr", "")) == call_addr
                    and row.get("mnemonic") == "CALL"
                    and "0x005b8ca0" in row.get("operands", "")
                    for row in rows
                ),
                f"missing fast trig call for {address} at {call_addr}",
                failures,
            )
        for forbidden in evidence["forbidden"]:
            require(
                not any(norm(row.get("instruction_addr", "")) == forbidden for row in rows),
                f"function boundary at {address} absorbed forbidden adjacent start {forbidden}",
                failures,
            )


def check_logs(failures: list[str]) -> None:
    expected = {
        "create-orphans-dry.log": "CreateFunctionsFromAddressList complete: mode=dry targets=4 created=0 would_create=4 already_exists=0 renamed=0 would_rename=0 failed=0",
        "apply-create-dry.log": "SUMMARY: updated=0 skipped=0 created=0 would_create=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "apply-create.log": "SUMMARY: updated=4 skipped=0 created=4 would_create=0 renamed=0 would_rename=0 signature_updated=4 comment_only_updated=0 missing=0 bad=0",
        "apply-create-final-dry.log": "SUMMARY: updated=0 skipped=4 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "apply-dry.log": "SUMMARY: updated=0 skipped=4 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=3 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=4 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-created-metadata.log": "targets=4 found=4 missing=0",
        "post-created-tags.log": "ExportFunctionTagsByAddress complete: rows=4 missing=0",
        "post-created-xrefs.log": "Wrote 4 rows",
        "post-created-body-instructions.log": "targets=4 missing=0",
        "post-created-decompile.log": "targets=4 dumped=4 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    queue_text = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave967.log")
    require("total_functions=6156 commented_functions=6156" in queue_text, "missing Wave967 quality export summary", failures)
    probe_text = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave967_queue_probe.log")
    require("Total functions: 6156" in probe_text, "missing Wave967 queue total", failures)
    require("Undefined signatures: 0" in probe_text, "missing Wave967 queue undefined count", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6156, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUALITY_TSV)
    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6156, "quality TSV row count mismatch", failures)
    require(commented == 6156, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6156, "strict clean-signature count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 173575047, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        CAMPAIGN,
        GHIDRA_REFERENCE,
        FUNCTION_INDEX,
        FASTVB_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-cfastvb-fast-trig-abi-review-wave967")
        == r"py -3 tools\ghidra_cfastvb_fast_trig_abi_review_wave967_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave967 CFastVB fast-trig ABI review" for row in ledger_rows), "missing Wave967 ledger row", failures)
    require(any(row.get("task") == "Wave967 CFastVB fast-trig ABI review" and row.get("attempt_id") == 20563 for row in attempt_rows), "missing Wave967 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_counts(failures)
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave967 CFastVB fast-trig ABI probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave967 CFastVB fast-trig ABI probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
