#!/usr/bin/env python3
"""Validate Wave970 CFastVB axis-dispatch continuation artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave970-cfastvb-axis-dispatch-continuation"
NOTE = ROOT / "release" / "readiness" / "ghidra_cfastvb_axis_dispatch_continuation_wave970_2026-05-28.md"
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

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260528-174057_post_wave970_cfastvb_axis_dispatch_continuation_verified"
TAG = "cfastvb-axis-dispatch-continuation-wave970"

EXPECTED_METADATA = {
    "0x005a46fc": (
        "CFastVB__DispatchOp_MultiplyQuaternionPair_Packed_005a46fc",
        "int CFastVB__DispatchOp_MultiplyQuaternionPair_Packed_005a46fc(void)",
        ("slot +0x4c", "0x0059850d", "sign masks", "0x005ef118", "FEMMS", "0x005a4792", "0x005a4795"),
    ),
    "0x005a4795": (
        "CFastVB__DispatchOp_NormalizeQuaternion_Packed_005a4795",
        "int CFastVB__DispatchOp_NormalizeQuaternion_Packed_005a4795(void)",
        ("slot +0x50", "0x00598514", "0x005ef170", "PFRSQRT", "PFRSQIT1", "PFRCPIT2", "0x005a47ef"),
    ),
    "0x005a4836": (
        "CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_Packed_005a4836",
        "int CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_Packed_005a4836(void)",
        ("slot +0x60", "0x00598530", "matrix-like", "0x005a4980", "0x005ef168", "0x005a4a4f"),
    ),
    "0x005a4a52": (
        "CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_FeatureOverride_005a4a52",
        "int CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_FeatureOverride_005a4a52(void)",
        ("slot +0x60", "0x005986a6", "feature bits 0x100 and 0x200", "PMOVMSKB", "PFCMPGE", "0x005a4c64"),
    ),
}

EXPECTED_XREFS = {
    "0x005a46fc": "0x0059850d",
    "0x005a4795": "0x00598514",
    "0x005a4836": "0x00598530",
    "0x005a4a52": "0x005986a6",
}

BODY_EVIDENCE = {
    "0x005a46fc": {"terminals": (("0x005a4792", "RET", "0xc"),), "forbidden": ("0x005a4795",)},
    "0x005a4795": {"terminals": (("0x005a47ef", "RET", "0x8"),), "forbidden": ("0x005a47f2",)},
    "0x005a4836": {
        "terminals": (
            ("0x005a4904", "RET", "0x8"),
            ("0x005a497d", "RET", "0x8"),
            ("0x005a49f1", "RET", "0x8"),
            ("0x005a4a4f", "RET", "0x8"),
        ),
        "required_internal": ("0x005a4980",),
        "forbidden": ("0x005a4a52",),
    },
    "0x005a4a52": {
        "terminals": (
            ("0x005a4b1d", "RET", "0x8"),
            ("0x005a4b92", "RET", "0x8"),
            ("0x005a4c06", "RET", "0x8"),
            ("0x005a4c64", "RET", "0x8"),
        ),
        "forbidden": ("0x005a4c67",),
    },
}

COMMON_TAGS = {
    "static-reaudit",
    TAG,
    "wave970-readback-verified",
    "retail-binary-evidence",
    "function-boundary-recovered",
    "dispatch-table-target",
    "cfastvb",
    "quaternion",
    "packed-mmx",
    "stack-locked",
    "comment-hardened",
    "signature-hardened",
}

CORE_TOKENS = (
    "Wave970",
    TAG,
    "0x005a46fc CFastVB__DispatchOp_MultiplyQuaternionPair_Packed_005a46fc",
    "0x005a4795 CFastVB__DispatchOp_NormalizeQuaternion_Packed_005a4795",
    "0x005a4836 CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_Packed_005a4836",
    "0x005a4a52 CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_FeatureOverride_005a4a52",
    "0x005a4980 internal branch target",
    "0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags",
    "344/1408 = 24.43%",
    "362/1426 = 25.39%",
    "6170/6170 = 100.00%",
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
        "pre-dispatch-slice-metadata.tsv": 7,
        "pre-dispatch-slice-xrefs.tsv": 7,
        "pre-dispatch-slice-instructions-around.tsv": 1827,
        "create-dispatch-slice-dry.tsv": 4,
        "post-metadata.tsv": 4,
        "post-tags.tsv": 4,
        "post-xrefs.tsv": 4,
        "post-body-instructions.tsv": 342,
        "post-decompile/index.tsv": 4,
    }
    for relative, count in expected.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == count, f"{relative} row count mismatch: {actual} != {count}", failures)


def check_artifacts(failures: list[str]) -> None:
    pre = {norm(row["address"]): row for row in read_tsv(BASE / "pre-dispatch-slice-metadata.tsv")}
    create_dry = {norm(row["address"]): row for row in read_tsv(BASE / "create-dispatch-slice-dry.tsv")}
    for address in EXPECTED_METADATA:
        row = pre.get(address)
        require(row is not None, f"missing pre metadata row for {address}", failures)
        if row:
            require(row.get("status") == "MISSING", f"pre metadata status mismatch at {address}", failures)
        dry_row = create_dry.get(address)
        require(dry_row is not None, f"missing dry-create row for {address}", failures)
        if dry_row:
            require(dry_row.get("status") == "would_create", f"dry-create status mismatch at {address}", failures)

    expanded_xrefs = {norm(row["target_addr"]): row for row in read_tsv(BASE / "pre-expanded-xrefs.tsv")}
    internal = expanded_xrefs.get("0x005a4980")
    require(internal is not None, "missing internal 0x005a4980 xref row", failures)
    if internal:
        require(internal.get("ref_type") == "CONDITIONAL_JUMP", "0x005a4980 xref should remain conditional jump only", failures)
        require(norm(internal.get("from_addr", "")) == "0x005a4915", "0x005a4980 branch source mismatch", failures)

    post = {norm(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {norm(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    xrefs = {norm(row["target_addr"]): row for row in read_tsv(BASE / "post-xrefs.tsv")}
    body = read_tsv(BASE / "post-body-instructions.tsv")
    decompile = {norm(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

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

    by_function: dict[str, list[dict[str, str]]] = {}
    for row in body:
        by_function.setdefault(norm(row.get("function_entry", "")), []).append(row)

    for address, evidence in BODY_EVIDENCE.items():
        rows = by_function.get(address, [])
        require(rows, f"missing body rows for {address}", failures)
        for terminal_addr, terminal_mnemonic, terminal_operand in evidence["terminals"]:
            require(
                any(
                    norm(row.get("instruction_addr", "")) == terminal_addr
                    and row.get("mnemonic") == terminal_mnemonic
                    and terminal_operand in row.get("operands", "")
                    for row in rows
                ),
                f"missing terminal evidence for {address}: {terminal_addr}",
                failures,
            )
        for internal_addr in evidence.get("required_internal", ()):
            require(
                any(norm(row.get("instruction_addr", "")) == internal_addr for row in rows),
                f"missing required internal target {internal_addr} inside {address}",
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
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 created=0 would_create=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=4 skipped=0 created=4 would_create=0 renamed=0 would_rename=0 signature_updated=4 comment_only_updated=8 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "create-dispatch-slice-dry.log": "CreateFunctionsFromAddressList complete: mode=dry targets=4 created=0 would_create=4 already_exists=0 renamed=0 would_rename=0 failed=0",
        "pre-dispatch-slice-metadata.log": "targets=7 found=3 missing=4",
        "pre-dispatch-slice-xrefs.log": "Wrote 7 rows",
        "pre-dispatch-slice-instructions-around.log": "Wrote 1827 instruction rows",
        "post-metadata.log": "targets=4 found=4 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=4 missing=0",
        "post-xrefs.log": "Wrote 4 rows",
        "post-body-instructions.log": "Wrote 342 function-body instruction rows",
        "post-decompile.log": "targets=4 dumped=4 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    queue_text = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave970.log")
    require("total_functions=6170 commented_functions=6170" in queue_text, "missing Wave970 quality export summary", failures)
    require("REPORT: Save succeeded" in queue_text, "missing Wave970 quality export save report", failures)
    probe_text = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave970_queue_probe.log")
    require("Total functions: 6170" in probe_text, "missing Wave970 queue total", failures)
    require("Undefined signatures: 0" in probe_text, "missing Wave970 queue undefined count", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6170, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUALITY_TSV)
    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6170, "quality TSV row count mismatch", failures)
    require(commented == 6170, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6170, "strict clean-signature count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 173607815, "backup byte count mismatch", failures)
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
        package.get("scripts", {}).get("test:ghidra-cfastvb-axis-dispatch-continuation-wave970")
        == r"py -3 tools\ghidra_cfastvb_axis_dispatch_continuation_wave970_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave970 CFastVB axis dispatch continuation" for row in ledger_rows), "missing Wave970 ledger row", failures)
    require(
        any(row.get("task") == "Wave970 CFastVB axis dispatch continuation" and row.get("attempt_id") == 20566 for row in attempt_rows),
        "missing Wave970 attempt row",
        failures,
    )


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
        print("Wave970 CFastVB axis-dispatch continuation probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave970 CFastVB axis-dispatch continuation probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
