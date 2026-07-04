#!/usr/bin/env python3
"""Validate Wave737 CFastVB fast-trig-tail read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave737-cfastvb-fast-trig-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cfastvb_fast_trig_tail_wave737_2026-05-22.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
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
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260522-123343_post_wave737_cfastvb_fast_trig_tail_verified"

SIGNATURE_TAGS = {
    "static-reaudit",
    "cfastvb-fast-trig-tail-wave737",
    "wave737-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "cfastvb-fast-trig-tail",
}

COMMENT_TAGS = {
    "static-reaudit",
    "cfastvb-fast-trig-tail-wave737",
    "wave737-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "comment-only",
    "locked-abi-comment-only",
    "cfastvb-fast-trig-tail",
}

TARGETS = {
    "0x005b81d0": (
        "CFastVB__SinCosApproxVec4_Paired",
        "void __stdcall CFastVB__SinCosApproxVec4_Paired(float * angle_vec4, float * out_sin_vec4, float * out_cos_vec4)",
        ("Wave737 static read-back", "RET 0xc", "out_sin_vec4", "out_cos_vec4"),
        SIGNATURE_TAGS | {"tranche-head", "vec4-sincos", "ret-0xc", "quaternion-euler-caller"},
    ),
    "0x005b83b9": (
        "CFastVB__SinCosVec4Approx",
        "void __stdcall CFastVB__SinCosVec4Approx(float * angle_vec4, float * out_sin_vec4, float * out_cos_vec4)",
        ("Wave737 static read-back", "RET 0xc", "0x0065eb90", "out_cos_vec4"),
        SIGNATURE_TAGS | {"vec4-sincos", "ret-0xc", "quaternion-euler-caller"},
    ),
    "0x005b85c0": (
        "Math__Atan2ApproxPacked",
        "int Math__Atan2ApproxPacked(void)",
        ("locked hidden MM0/MM1", "stale EAX-style return", "current signature is intentionally retained"),
        COMMENT_TAGS | {"atan2-approx", "packed-mmx", "ret-plain"},
    ),
    "0x005b86c0": (
        "CFastVB__FastAcosApprox_Scalar",
        "int CFastVB__FastAcosApprox_Scalar(void)",
        ("locked hidden MM0", "reciprocal-square-root", "current signature is intentionally retained"),
        COMMENT_TAGS | {"acos-approx", "packed-mmx", "ret-plain"},
    ),
    "0x005b8ca0": (
        "CFastVB__FastTrigPairApprox_Scalar",
        "uint CFastVB__FastTrigPairApprox_Scalar(void)",
        ("no-function call sites", "0x0065ee50", "neighboring boundaries are proven"),
        COMMENT_TAGS | {"trig-pair-approx", "packed-mmx", "ret-plain"},
    ),
    "0x005b8da0": (
        "CFastVB__FastSinApprox_Scalar_005b8da0",
        "uint CFastVB__FastSinApprox_Scalar_005b8da0(void)",
        ("fast sine-style", "packed register ABI", "current signature"),
        COMMENT_TAGS | {"tranche-tail", "sin-approx", "packed-mmx", "ret-plain"},
    ),
}

DOC_TOKENS = (
    "Wave737 CFastVB fast trig tail",
    "cfastvb-fast-trig-tail-wave737",
    "0x005b81d0 CFastVB__SinCosApproxVec4_Paired",
    "0x005b83b9 CFastVB__SinCosVec4Approx",
    "0x005b85c0 Math__Atan2ApproxPacked",
    "0x005b86c0 CFastVB__FastAcosApprox_Scalar",
    "0x005b8ca0 CFastVB__FastTrigPairApprox_Scalar",
    "0x005b8da0 CFastVB__FastSinApprox_Scalar_005b8da0",
    "0x005bb9b0 CDXTexture__InverseDct8x8_DequantAndStore_Scalar",
    "0x0042f220 CSPtrSet__Clear",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime math behavior proven",
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
        "pre-metadata.tsv": 6,
        "pre-tags.tsv": 6,
        "pre-xrefs.tsv": 30,
        "pre-instructions.tsv": 1686,
        "pre-decompile/index.tsv": 6,
        "caller-decompile/index.tsv": 9,
        "xref-site-instructions.tsv": 1110,
        "post-metadata.tsv": 6,
        "post-tags.tsv": 6,
        "post-xrefs.tsv": 30,
        "post-instructions.tsv": 1686,
        "post-decompile/index.tsv": 6,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, (name, signature, comment_tokens, expected_tags) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch at {address}", failures)
        require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
        comment = row.get("comment", "")
        require("static retail ghidra metadata" in comment.lower(), f"missing static-evidence boundary at {address}", failures)
        require("runtime math behavior" in comment, f"missing runtime boundary at {address}", failures)
        for token in comment_tokens:
            require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(expected_tags.issubset(actual_tags), f"tags missing at {address}: {expected_tags - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)
        require((BASE / "post-decompile" / f"{address[2:]}_{name}.c").is_file(), f"missing decompile file for {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=4 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=4 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "pre-metadata.log": "targets=6 found=6 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "pre-xrefs.log": "Wrote 30 rows",
        "pre-instructions.log": "Wrote 1686 instruction rows",
        "pre-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "caller-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
        "xref-site-instructions.log": "Wrote 1110 instruction rows",
        "post-metadata.log": "targets=6 found=6 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "post-xrefs.log": "Wrote 30 rows",
        "post-instructions.log": "Wrote 1686 instruction rows",
        "post-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=4339",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}", failures)
        require("REPORT: Save succeeded" in text, f"missing save evidence in {relative}", failures)
        require("LockException" not in text, f"unexpected LockException in {relative}", failures)
        require("MISSING:" not in text, f"unexpected MISSING in {relative}", failures)
        require("BADNAME" not in text, f"unexpected BADNAME in {relative}", failures)
        require("Invalid script" not in text, f"unexpected Invalid script in {relative}", failures)
        require("Input file not found" not in text, f"unexpected missing input in {relative}", failures)

    require("targets=30 missing=0" in read_text(BASE / "xref-site-instructions.log"), "missing xref-site target count", failures)
    for relative in ("apply-dry.log", "apply.log", "apply-final-dry.log"):
        text = read_text(BASE / relative)
        require("FAIL:" not in text, f"unexpected FAIL in accepted log {relative}", failures)
        require("SCRIPT ERROR" not in text, f"unexpected SCRIPT ERROR in accepted log {relative}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 1759, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 1216, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 43, "param count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005bb9b0", "high-signal head address mismatch", failures)
    require(high_signal["name"] == "CDXTexture__InverseDct8x8_DequantAndStore_Scalar", "high-signal head name mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_head = next(row for row in rows if not row.get("comment", "").strip())
    require(commented == 4339, "commented count mismatch", failures)
    require(strict_clean == 4281, "strict clean-signature proxy mismatch", failures)
    require(raw_head["address"] == "0x0042f220", "raw commentless head address mismatch", failures)
    require(raw_head["name"] == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)

    for address in TARGETS:
        row = next((item for item in rows if normalize_address(item["address"]) == address), None)
        require(row is not None, f"missing queue row {address}", failures)
        if row is not None:
            require(bool(row.get("comment", "").strip()), f"queue row still commentless {address}", failures)
            require(row["signature"] == TARGETS[address][1], f"queue signature mismatch {address}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("Destination") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("FileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("TotalBytes") == 166955911, "backup byte count mismatch", failures)
    require(backup.get("DiffCount") == 0, "backup diff count mismatch", failures)


def check_docs_and_state(failures: list[str]) -> None:
    docs = (
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        FASTVB_DOC,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    )
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            escaped_token = token.replace("\\", "\\\\")
            require(
                token in text or escaped_token in text,
                f"missing doc token in {path.relative_to(ROOT)}: {token}",
                failures,
            )
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {token}", failures)

    package = read_text(PACKAGE_JSON)
    require("test:ghidra-cfastvb-fast-trig-tail-wave737" in package, "missing npm wrapper", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave737 CFastVB fast trig tail" for row in ledger_rows), "missing ledger row", failures)
    require(any(row.get("task") == "Wave737 CFastVB fast trig tail" and row.get("readback") == "verified" for row in attempt_rows), "missing attempt log row", failures)

    tracking = read_json(TRACKING)
    require(tracking.get("last_completed", {}).get("task") == "Wave737 CFastVB fast trig tail", "tracking last_completed mismatch", failures)
    require(tracking.get("next_attempt_id") == 20393, "tracking next_attempt_id mismatch", failures)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    failures: list[str] = []
    for check in (check_artifacts, check_logs, check_queue_and_backup, check_docs_and_state):
        try:
            check(failures)
        except Exception as exc:
            failures.append(f"{check.__name__}: {exc}")

    if failures:
        print("Wave737 CFastVB fast trig tail probe FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave737 CFastVB fast trig tail probe PASS")
    print(f"Targets: {len(TARGETS)}")
    print("Queue: 6098 total, 4339 commented, 1759 commentless, 1216 undefined, 43 param_N")
    print(f"Backup: {BACKUP_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
