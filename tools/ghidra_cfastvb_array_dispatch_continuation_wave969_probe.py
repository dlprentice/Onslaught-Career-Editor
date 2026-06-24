#!/usr/bin/env python3
"""Validate Wave969 CFastVB array-dispatch continuation artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave969-cfastvb-array-dispatch-continuation"
NOTE = ROOT / "release" / "readiness" / "ghidra_cfastvb_array_dispatch_continuation_wave969_2026-05-28.md"
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

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260528-170703_post_wave969_cfastvb_array_dispatch_continuation_verified"
TAG = "cfastvb-array-dispatch-continuation-wave969"

EXPECTED_METADATA = {
    "0x005a3a40": (
        "CFastVB__DispatchOp_TransformVec2ArrayByMatrix4_WithTranslation_005a3a40",
        "int CFastVB__DispatchOp_TransformVec2ArrayByMatrix4_WithTranslation_005a3a40(void)",
        ("slot +0xec", "0x005986cf", "0x005aa73b", "Vec2 inputs", "translation terms", "0x005a3c9c"),
    ),
    "0x005a3ca0": (
        "CFastVB__DispatchOp_TransformProjectVec2ArrayByMatrix4_005a3ca0",
        "int CFastVB__DispatchOp_TransformProjectVec2ArrayByMatrix4_005a3ca0(void)",
        ("slot +0xf0", "0x005986d9", "0x005aa7c9", "RCPPS/SUBPS/MULPS", "projected Vec2", "0x005a3ee2"),
    ),
    "0x005a3f00": (
        "CFastVB__DispatchOp_TransformVec2ArrayByMatrix4_NoTranslation_005a3f00",
        "int CFastVB__DispatchOp_TransformVec2ArrayByMatrix4_NoTranslation_005a3f00(void)",
        ("slot +0xf4", "0x005986e3", "0x005aa790", "without translation terms", "Vec2 output", "0x005a40b3"),
    ),
    "0x005a4160": (
        "CFastVB__DispatchOp_TransformProjectVec3ArrayByMatrix4_Alt_005a4160",
        "int CFastVB__DispatchOp_TransformProjectVec3ArrayByMatrix4_Alt_005a4160(void)",
        ("slot +0xfc", "0x005986bb", "0x005a9f3f", "RCPPS/SUBPS/MULPS", "projected Vec3", "0x005a447a"),
    ),
    "0x005a4480": (
        "CFastVB__DispatchOp_TransformVec3ArrayByMatrix4_NoTranslation_005a4480",
        "int CFastVB__DispatchOp_TransformVec3ArrayByMatrix4_NoTranslation_005a4480(void)",
        ("slot +0x100", "0x005986c5", "0x005a99f8", "without translation terms", "Vec3-style output", "0x005a46f9"),
    ),
}

EXPECTED_XREFS = {
    "0x005a3a40": "0x005986cf",
    "0x005a3ca0": "0x005986d9",
    "0x005a3f00": "0x005986e3",
    "0x005a4160": "0x005986bb",
    "0x005a4480": "0x005986c5",
}

BODY_EVIDENCE = {
    "0x005a3a40": {"terminal": ("0x005a3c9c", "RET", "0x18"), "forbidden": ("0x005a3ca0",)},
    "0x005a3ca0": {"terminal": ("0x005a3ee2", "RET", "0x18"), "forbidden": ("0x005a3f00",)},
    "0x005a3f00": {"terminal": ("0x005a40b3", "RET", "0x18"), "forbidden": ("0x005a40c0",)},
    "0x005a4160": {"terminal": ("0x005a447a", "RET", "0x18"), "forbidden": ("0x005a4480",)},
    "0x005a4480": {"terminal": ("0x005a46f9", "RET", "0x18"), "forbidden": ("0x005a46fc",)},
}

COMMON_TAGS = {
    "static-reaudit",
    TAG,
    "wave969-readback-verified",
    "retail-binary-evidence",
    "function-boundary-recovered",
    "dispatch-table-target",
    "cfastvb",
    "array-transform",
    "packed-sse",
    "stack-locked",
    "comment-hardened",
    "signature-hardened",
}

CORE_TOKENS = (
    "Wave969",
    TAG,
    "0x005a3a40 CFastVB__DispatchOp_TransformVec2ArrayByMatrix4_WithTranslation_005a3a40",
    "0x005a3ca0 CFastVB__DispatchOp_TransformProjectVec2ArrayByMatrix4_005a3ca0",
    "0x005a3f00 CFastVB__DispatchOp_TransformVec2ArrayByMatrix4_NoTranslation_005a3f00",
    "0x005a4160 CFastVB__DispatchOp_TransformProjectVec3ArrayByMatrix4_Alt_005a4160",
    "0x005a4480 CFastVB__DispatchOp_TransformVec3ArrayByMatrix4_NoTranslation_005a4480",
    "0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags",
    "344/1408 = 24.43%",
    "358/1422 = 25.18%",
    "6166/6166 = 100.00%",
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
        "pre-candidate-metadata.tsv": 5,
        "pre-candidate-xrefs.tsv": 5,
        "pre-candidate-around.tsv": 805,
        "pre-candidate-around-wide.tsv": 1705,
        "create-candidates-dry.tsv": 5,
        "post-metadata.tsv": 5,
        "post-tags.tsv": 5,
        "post-xrefs.tsv": 5,
        "post-body-instructions.tsv": 691,
        "post-decompile/index.tsv": 5,
    }
    for relative, count in expected.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == count, f"{relative} row count mismatch: {actual} != {count}", failures)


def check_artifacts(failures: list[str]) -> None:
    pre_missing = {norm(row["address"]): row for row in read_tsv(BASE / "pre-candidate-metadata.tsv")}
    create_dry = {norm(row["address"]): row for row in read_tsv(BASE / "create-candidates-dry.tsv")}
    for address in EXPECTED_METADATA:
        row = pre_missing.get(address)
        require(row is not None, f"missing pre-candidate metadata row for {address}", failures)
        if row:
            require(row.get("status") == "MISSING", f"pre-candidate status mismatch at {address}", failures)
        dry_row = create_dry.get(address)
        require(dry_row is not None, f"missing dry-create row for {address}", failures)
        if dry_row:
            require(dry_row.get("status") == "would_create", f"dry-create status mismatch at {address}", failures)

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
        for forbidden in evidence["forbidden"]:
            require(
                not any(norm(row.get("instruction_addr", "")) == forbidden for row in rows),
                f"function boundary at {address} absorbed forbidden adjacent start {forbidden}",
                failures,
            )


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 created=0 would_create=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=5 skipped=0 created=5 would_create=0 renamed=0 would_rename=0 signature_updated=5 comment_only_updated=10 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "create-candidates-dry.log": "CreateFunctionsFromAddressList complete: mode=dry targets=5 created=0 would_create=5 already_exists=0 renamed=0 would_rename=0 failed=0",
        "pre-candidate-metadata.log": "targets=5 found=0 missing=5",
        "pre-candidate-xrefs.log": "Wrote 5 rows",
        "pre-candidate-around.log": "Wrote 805 instruction rows",
        "pre-candidate-around-wide.log": "Wrote 1705 instruction rows",
        "post-metadata.log": "targets=5 found=5 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=5 missing=0",
        "post-xrefs.log": "Wrote 5 rows",
        "post-body-instructions.log": "Wrote 691 function-body instruction rows",
        "post-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    queue_text = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave969.log")
    require("total_functions=6166 commented_functions=6166" in queue_text, "missing Wave969 quality export summary", failures)
    require("REPORT: Save succeeded" in queue_text, "missing Wave969 quality export save report", failures)
    probe_text = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave969_queue_probe.log")
    require("Total functions: 6166" in probe_text, "missing Wave969 queue total", failures)
    require("Undefined signatures: 0" in probe_text, "missing Wave969 queue undefined count", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6166, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUALITY_TSV)
    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6166, "quality TSV row count mismatch", failures)
    require(commented == 6166, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6166, "strict clean-signature count mismatch", failures)

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
        package.get("scripts", {}).get("test:ghidra-cfastvb-array-dispatch-continuation-wave969")
        == r"py -3 tools\ghidra_cfastvb_array_dispatch_continuation_wave969_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave969 CFastVB array dispatch continuation" for row in ledger_rows), "missing Wave969 ledger row", failures)
    require(
        any(row.get("task") == "Wave969 CFastVB array dispatch continuation" and row.get("attempt_id") == 20565 for row in attempt_rows),
        "missing Wave969 attempt row",
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
        print("Wave969 CFastVB array-dispatch continuation probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave969 CFastVB array-dispatch continuation probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
