#!/usr/bin/env python3
"""Validate Wave898 CFastVB compose-transform read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave898-cfastvb-compose-transform-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cfastvb_compose_transform_tail_wave898_2026-05-26.md"
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

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260526-080711_post_wave898_cfastvb_compose_transform_tail_verified"
COMMON_TAGS = {
    "static-reaudit",
    "cfastvb-compose-transform-tail-wave898",
    "wave898-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-verified",
    "important-cfastvb-math-infrastructure",
    "raw-commentless-tail",
    "compose-transform-tail",
}
TARGETS = {
    "0x005a9f44": {
        "name": "CFastVB__DispatchOp_ComposeTransformAndProjectVec3_005a9f44",
        "signature": "int CFastVB__DispatchOp_ComposeTransformAndProjectVec3_005a9f44(void)",
        "tokens": ("Wave898 static read-back", "0x005984ea", "0x005aa0ac", "CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a9ced"),
        "xrefs": {"0x005984ea"},
        "extra_tags": {"dispatch-table-data-xref", "matrix-compose", "projected-vec3-remap"},
    },
    "0x005aa0cc": {
        "name": "CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Scalar",
        "signature": "int CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Scalar(void)",
        "tokens": ("Wave898 static read-back", "0x005984f1", "0x005aa2d2", "CFastVB__DispatchOp_InvertMatrix4x4_Variant_005a9637"),
        "xrefs": {"0x005984f1"},
        "extra_tags": {"dispatch-table-data-xref", "scalar-compose-transform", "matrix-inverse"},
    },
    "0x005aa2f2": {
        "name": "CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_SIMD",
        "signature": "int CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_SIMD(void)",
        "tokens": ("Wave898 static read-back", "0x00598684", "0x005aa424", "CFastVB__DispatchOp_InvertMatrix4x4_WithDeterminant_005a8f5d"),
        "xrefs": {"0x00598684"},
        "extra_tags": {"dispatch-table-data-xref", "simd-compose-transform", "matrix-inverse"},
    },
}
CONTEXT_NAMES = {
    "CFastVB__InitDispatchOpsFromFeatureFlags",
    "CFastVB__DispatchOp_MultiplyMatrix4x4_Packed_005a9d78",
    "CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a9ced",
    "CFastVB__DispatchOp_InvertMatrix4x4_Variant_005a9637",
    "CFastVB__DispatchOp_InvertMatrix4x4_WithDeterminant_005a8f5d",
    "CFastVB__DispatchOp_InitIdentityMatrix4x4_005a62bf",
    "CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Core_005a647f",
    "CFastVB__DispatchOp_ComposeMatrixFromOptionalTransforms",
}
CORE_ANCHORS = (
    "Wave898 CFastVB compose transform tail",
    "cfastvb-compose-transform-tail-wave898",
    "0x005a9f44 CFastVB__DispatchOp_ComposeTransformAndProjectVec3_005a9f44",
    "0x005aa0cc CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Scalar",
    "0x005aa2f2 CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_SIMD",
    "0x005b7770 CDXTexture__ValidateJpegFrameAndComputeMcuLayout",
    "6100/6113 = 99.79%",
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
        "pre-metadata.tsv": 3,
        "pre-tags.tsv": 3,
        "pre-xrefs.tsv": 3,
        "pre-instructions.tsv": 444,
        "pre-decompile/index.tsv": 3,
        "pre-context-metadata.tsv": 8,
        "post-metadata.tsv": 3,
        "post-tags.tsv": 3,
        "post-xrefs.tsv": 3,
        "post-instructions.tsv": 444,
        "post-decompile/index.tsv": 3,
        "post-context-metadata.tsv": 8,
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

    context_names = {row.get("name", "") for row in read_tsv(BASE / "post-context-metadata.tsv")}
    for name in CONTEXT_NAMES:
        require(name in context_names, f"missing context metadata: {name}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=3 renamed=0 would_rename=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=3 skipped=0 renamed=0 would_rename=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=3 renamed=0 would_rename=0 missing=0 bad=0",
        "post-metadata.log": "targets=3 found=3 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=3 missing=0",
        "post-xrefs.log": "Wrote 3 rows",
        "post-instructions.log": "Wrote 444 function-body instruction rows",
        "post-decompile.log": "targets=3 dumped=3 missing=0 failed=0",
        "post-context-metadata.log": "targets=8 found=8 missing=0",
        "quality-refresh.log": "total_functions=6113 commented_functions=6100",
        "queue-probe.log": "Commentless functions: 13",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave898.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave898_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "Invalid script", "MISSING:", "BADSIG:", "BADNAME", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6113, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 13, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6113, "quality TSV row count mismatch", failures)
    require(commented == 6100, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6100, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x005b7770", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CDXTexture__ValidateJpegFrameAndComputeMcuLayout", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173214599, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [PUBLIC_NOTE, FUNCTION_INDEX, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG, FASTVB_DOC, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE]
    for path in docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-cfastvb-compose-transform-tail-wave898")
        == r"py -3 tools\ghidra_cfastvb_compose_transform_tail_wave898_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave898 CFastVB compose transform tail" for row in ledger_rows), "missing Wave898 ledger row", failures)
    require(
        any(row.get("task") == "Wave898 CFastVB compose transform tail" and row.get("attempt_id") == 20553 for row in attempts),
        "missing Wave898 attempt row",
        failures,
    )


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
        print("Wave898 CFastVB compose-transform probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave898 CFastVB compose-transform probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
