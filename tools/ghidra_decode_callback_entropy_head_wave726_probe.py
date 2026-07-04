#!/usr/bin/env python3
"""Validate Wave726 decode callback/entropy head read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave726-decode-callback-entropy-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_decode_callback_entropy_head_wave726_2026-05-22.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
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
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

SIGNATURE_TAGS = {
    "static-reaudit",
    "decode-callback-entropy-head-wave726",
    "wave726-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "decode-callback-entropy",
}

COMMENT_TAGS = {
    "static-reaudit",
    "decode-callback-entropy-head-wave726",
    "wave726-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "comment-only",
    "hidden-register-context",
    "decode-callback-entropy",
}

TARGETS = {
    "0x005ad550": (
        "CTexture__InitDecodeCallbackTables",
        "void __stdcall CTexture__InitDecodeCallbackTables(void * decode_context)",
        ("initializes the texture decode callback table", "0xe8-byte callback/controller table", "RET 0x4 evidence"),
        SIGNATURE_TAGS | {"callback-table", "decode-pipeline", "ret-0x4", "tranche-head"},
    ),
    "0x005ad590": (
        "CFastVB__JpegEntropy_CommitAndResetBlockState",
        "int CFastVB__JpegEntropy_CommitAndResetBlockState(void)",
        ("commits and resets JPEG entropy block state", "hidden EBX texture/decode context", "current int(void) signature is intentionally retained"),
        COMMENT_TAGS | {"entropy", "commit-reset", "hidden-ebx-context"},
    ),
    "0x005ae190": (
        "CDXTexture__InitBlockCoefficientHistory",
        "void __stdcall CDXTexture__InitBlockCoefficientHistory(void * decode_context)",
        ("initializes block coefficient history resources", "0x40-byte controller", "0xffffffff"),
        SIGNATURE_TAGS | {"coefficient-history", "allocator", "ret-0x4"},
    ),
    "0x005ae600": (
        "CDXTexture__InitPerComponentCoefficientBuffers",
        "void __stdcall CDXTexture__InitPerComponentCoefficientBuffers(void * decode_context)",
        ("initializes per-component coefficient buffers", "0x54-byte controller", "component descriptor at +0x50"),
        SIGNATURE_TAGS | {"component-coefficients", "allocator", "ret-0x4"},
    ),
    "0x005ae780": (
        "CDXTexture__InitScanlineOutputStage",
        "void __stdcall CDXTexture__InitScanlineOutputStage(void * decode_context)",
        ("initializes the scanline output stage", "hidden ESI mode", "0x1c-byte stage"),
        SIGNATURE_TAGS | {"scanline-output", "hidden-esi-mode", "allocator", "ret-0x4"},
    ),
    "0x005ae810": (
        "CDXTexture__RefillEntropyInputWindow",
        "int CDXTexture__RefillEntropyInputWindow(void)",
        ("refills/copies from the entropy input window", "hidden EBP progress state", "current int(void) signature is intentionally retained"),
        COMMENT_TAGS | {"entropy-input-window", "hidden-ebp-context", "stack-locked-abi", "tranche-tail"},
    ),
}

DOC_TOKENS = (
    "Wave726 decode callback/entropy head",
    "decode-callback-entropy-head-wave726",
    "0x005ad550 CTexture__InitDecodeCallbackTables",
    "0x005ad590 CFastVB__JpegEntropy_CommitAndResetBlockState",
    "0x005ae190 CDXTexture__InitBlockCoefficientHistory",
    "0x005ae600 CDXTexture__InitPerComponentCoefficientBuffers",
    "0x005ae780 CDXTexture__InitScanlineOutputStage",
    "0x005ae810 CDXTexture__RefillEntropyInputWindow",
    "0x005aeaf0 CDXTexture__UpsampleChromaLinearHorizontal",
    "0x0042f220 CSPtrSet__Clear",
    r"[maintainer-local-ghidra-backup-root]\BEA_20260522-065624_post_wave726_decode_callback_entropy_head_verified",
)

OVERCLAIM_TOKENS = (
    "runtime jpeg decode behavior proven",
    "runtime decode behavior proven",
    "runtime image decode behavior proven",
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


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 6,
        "pre-tags.tsv": 6,
        "pre-xrefs.tsv": 9,
        "pre-instructions.tsv": 3246,
        "pre-decompile/index.tsv": 6,
        "post-metadata.tsv": 6,
        "post-tags.tsv": 6,
        "post-xrefs.tsv": 9,
        "post-instructions.tsv": 3246,
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
        require("Wave726 static read-back" in comment, f"missing Wave726 comment at {address}", failures)
        require("Static retail Ghidra metadata" in comment, f"missing static-evidence boundary at {address}", failures)
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
        "apply-dry.log": "SUMMARY: updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=4 comment_only_updated=2 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=4 comment_only_updated=2 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "pre-metadata.log": "targets=6 found=6 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "pre-xrefs.log": "Wrote 9 rows",
        "pre-instructions.log": "Wrote 3246 instruction rows",
        "pre-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "post-metadata.log": "targets=6 found=6 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "post-xrefs.log": "Wrote 9 rows",
        "post-instructions.log": "Wrote 3246 instruction rows",
        "post-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}", failures)
        require("LockException" not in text, f"unexpected LockException in {relative}", failures)
        require("MISSING:" not in text, f"unexpected MISSING in {relative}", failures)
        require("BADNAME" not in text, f"unexpected BADNAME in {relative}", failures)
        require("FAIL" not in text, f"unexpected FAIL in {relative}", failures)
        require("Invalid script" not in text, f"unexpected invalid script in {relative}", failures)
        require("Input file not found" not in text, f"stale failed export in {relative}", failures)

    require("REPORT: Save succeeded" in read_text(BASE / "apply.log"), "missing apply save evidence", failures)
    require("REPORT: Save succeeded" in read_text(BASE / "apply-final-dry.log"), "missing final dry save evidence", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 1824, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 1216, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 99, "param count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005aeaf0", "high-signal head address mismatch", failures)
    require(high_signal["name"] == "CDXTexture__UpsampleChromaLinearHorizontal", "high-signal head name mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    raw_head = next(row for row in rows if not row.get("comment", "").strip())
    require(commented == 4274, "commented count mismatch", failures)
    require(strict_clean == 4216, "strict clean-signature proxy mismatch", failures)
    require(raw_head["address"] == "0x0042f220", "raw commentless head address mismatch", failures)
    require(raw_head["name"] == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)

    by_address = {normalize_address(row["address"]): row for row in rows}
    for address in TARGETS:
        row = by_address.get(address)
        require(row is not None, f"missing queue row for {address}", failures)
        if row is None:
            continue
        require(bool(row.get("comment", "").strip()), f"queue row still commentless for {address}", failures)
        if address in {"0x005ad550", "0x005ae190", "0x005ae600", "0x005ae780"}:
            require(re.search(r"\bparam_\d+\b", row.get("signature", "")) is None, f"queue row still has param_N for {address}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup["backup"] == r"[maintainer-local-ghidra-backup-root]\BEA_20260522-065624_post_wave726_decode_callback_entropy_head_verified", "backup destination mismatch", failures)
    require(backup["fileCount"] == 19, "backup file count mismatch", failures)
    require(int(backup["totalBytes"]) == 166595463, "backup byte count mismatch", failures)
    require(backup["diffCount"] == 0, "backup diff count mismatch", failures)


def check_docs_and_state(failures: list[str]) -> None:
    docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        DXTEXTURE_DOC,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            escaped = token.replace("\\", "\\\\")
            require(token in text or escaped in text, f"missing doc token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lower, f"overclaim token in {path.relative_to(ROOT)}: {token}", failures)

    require("test:ghidra-decode-callback-entropy-head-wave726" in read_text(PACKAGE_JSON), "missing package script", failures)

    ledgers = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave726 decode callback/entropy head" for row in ledgers), "missing Wave726 ledger row", failures)
    require(any(row.get("attempt_id") == 20381 and row.get("task") == "Wave726 decode callback/entropy head" for row in attempts), "missing Wave726 attempt row", failures)

    tracking = read_json(TRACKING)
    require(tracking["next_attempt_id"] == 20382, "tracking next_attempt_id mismatch", failures)
    require("Wave726 decode callback/entropy head" in tracking.get("current_focus", ""), "tracking focus mismatch", failures)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Return non-zero when validation fails.")
    args = parser.parse_args(argv)

    failures: list[str] = []
    for check in (check_artifacts, check_logs, check_queue_and_backup, check_docs_and_state):
        try:
            check(failures)
        except Exception as exc:  # pragma: no cover - diagnostic path
            failures.append(f"{check.__name__}: {exc}")

    if failures:
        print("Wave726 decode callback/entropy head probe")
        print("Status: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0

    print("Wave726 decode callback/entropy head probe")
    print("Status: PASS")
    print("Targets: 6")
    print("Queue: 6098 total, 4274 commented, 1824 commentless, 1216 undefined, 99 param_N")
    print(r"Backup: [maintainer-local-ghidra-backup-root]\BEA_20260522-065624_post_wave726_decode_callback_entropy_head_verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
