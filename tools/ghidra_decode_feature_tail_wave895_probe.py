#!/usr/bin/env python3
"""Validate Wave895 decode-feature-tail read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave895-decode-feature-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_decode_feature_tail_wave895_2026-05-26.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
TEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "texture.cpp" / "_index.md"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

TASK = "Wave895 decode feature tail"
TAG = "decode-feature-tail-wave895"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260526-064920_post_wave895_decode_feature_tail_verified"
STRICT_PROXY = "6086/6113 = 99.56%"
NEXT_HEAD = "0x0059c610 CFastVB__ReleaseOwnedObjectAndReset_Core"

TARGETS = {
    "0x00598390": ("CFastVB__DetectCpuFeatureMask", "int CFastVB__DetectCpuFeatureMask(void)", ("CPUID", "0x00598474", "AuthenticAMD", "0x100/0x200")),
    "0x0059a71a": ("CFastVB__SelectBestNodeTreeMatch", "int CFastVB__SelectBestNodeTreeMatch(void)", ("Wave709", "0xbbd/0xbfb/0xbbc/0xc06", "-0x7ff8fff2")),
    "0x0059b150": ("CTexture__InitDecodeLookupScratchTables", "void CTexture__InitDecodeLookupScratchTables(void)", ("Wave710", "hidden EAX", "0xffffffff")),
    "0x0059b1d0": ("CTexture__InitializeDecodePipelineFromHeader", "void CTexture__InitializeDecodePipelineFromHeader(void)", ("0x0059b4f9", "0x2f/0x30/1", "vtable")),
    "0x0059b510": ("CDXTexture__ValidateJpegFrameAndBuildScanLayout", "void CDXTexture__ValidateJpegFrameAndBuildScanLayout(void)", ("0x0059b9e2", "0xffdc", "CDXTexture__CeilDiv")),
    "0x0059b6f0": ("CTexture__BuildComponentPlaneLayoutTables", "uint CTexture__BuildComponentPlaneLayoutTables(void)", ("0x0059b926", "state+0x5b", "0x0d")),
    "0x0059b880": ("CTexture__EnsureComponentDecodeScratchBlocks", "void CTexture__EnsureComponentDecodeScratchBlocks(void)", ("0x0059b92d", "0x34", "0x21 dwords")),
    "0x0059be00": ("CDXTexture__CreateDecodeJobDescriptor", "int CDXTexture__CreateDecodeJobDescriptor(void)", ("Wave711", "0x0059c563", "0x248")),
    "0x0059be70": ("CDXTexture__AllocDecodeBlockAndLink", "int CDXTexture__AllocDecodeBlockAndLink(void)", ("Wave711", "0x0059c56a", "0x248")),
}

EXPECTED_XREFS = {
    "0x00598390": [("0x00598474", "CFastVB__InitDispatchOpsFromFeatureFlags", "UNCONDITIONAL_CALL")],
    "0x0059a71a": [
        ("0x00599576", "CDXTexture__ProcessTextureChunkAndEmitBindings", "UNCONDITIONAL_CALL"),
        ("0x00599349", "CTexture__ValidateConstantRegisterDeclarationType", "UNCONDITIONAL_CALL"),
    ],
    "0x0059b150": [("0x0059b1e0", "CTexture__InitializeDecodePipelineFromHeader", "UNCONDITIONAL_CALL")],
    "0x0059b1d0": [("0x0059b4f9", "CTexture__CreateDecodeDispatchContext", "UNCONDITIONAL_CALL")],
    "0x0059b510": [("0x0059b9e2", "CDXTexture__DecodeState_AdvanceFrame", "UNCONDITIONAL_CALL")],
    "0x0059b6f0": [("0x0059b926", "CDXTexture__DecodeState_RunPostFrameCallbacks", "UNCONDITIONAL_CALL")],
    "0x0059b880": [("0x0059b92d", "CDXTexture__DecodeState_RunPostFrameCallbacks", "UNCONDITIONAL_CALL")],
    "0x0059be00": [("0x0059c563", "CDXTexture__InitDecodeAllocatorVtable", "DATA")],
    "0x0059be70": [("0x0059c56a", "CDXTexture__InitDecodeAllocatorVtable", "DATA")],
}

COMMON_TAGS = {
    "static-reaudit",
    TAG,
    "wave895-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-verified",
    "important-texture-decode-infrastructure",
    "raw-commentless-tail",
}

CORE_ANCHORS = (
    TASK,
    TAG,
    "0x00598390 CFastVB__DetectCpuFeatureMask",
    "0x0059a71a CFastVB__SelectBestNodeTreeMatch",
    "0x0059b150 CTexture__InitDecodeLookupScratchTables",
    "0x0059b1d0 CTexture__InitializeDecodePipelineFromHeader",
    "0x0059b510 CDXTexture__ValidateJpegFrameAndBuildScanLayout",
    "0x0059b6f0 CTexture__BuildComponentPlaneLayoutTables",
    "0x0059b880 CTexture__EnsureComponentDecodeScratchBlocks",
    "0x0059be00 CDXTexture__CreateDecodeJobDescriptor",
    "0x0059be70 CDXTexture__AllocDecodeBlockAndLink",
    NEXT_HEAD,
    STRICT_PROXY,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
    "exact layout proven",
    "exact source identity proven",
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
        "targets-snapshot.tsv": 9,
        "pre-metadata.tsv": 9,
        "pre-tags.tsv": 9,
        "pre-xrefs.tsv": 10,
        "pre-instructions.tsv": 1329,
        "pre-decompile/index.tsv": 9,
        "post-metadata.tsv": 9,
        "post-tags.tsv": 9,
        "post-xrefs.tsv": 10,
        "post-instructions.tsv": 1329,
        "post-decompile/index.tsv": 9,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs_by_target: dict[str, list[dict[str, str]]] = {}
    for row in read_tsv(BASE / "post-xrefs.tsv"):
        xrefs_by_target.setdefault(normalize_address(row["target_addr"]), []).append(row)

    for address, (name, signature, tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in ("Wave895 static read-back", "Static retail Ghidra evidence only", "remain unproven", *tokens):
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        actual = {(normalize_address(x.get("from_addr", "")), x.get("from_function"), x.get("ref_type")) for x in xrefs_by_target.get(address, [])}
        for expected_from, expected_function, expected_type in EXPECTED_XREFS[address]:
            require((expected_from, expected_function, expected_type) in actual, f"missing xref at {address}: {expected_from}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=9 renamed=0 would_rename=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=9 skipped=0 renamed=0 would_rename=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=9 renamed=0 would_rename=0 missing=0 bad=0",
        "post-metadata.log": "targets=9 found=9 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=9 missing=0",
        "post-xrefs.log": "Wrote 10 rows",
        "post-instructions.log": "Wrote 1329 function-body instruction rows",
        "post-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6113 commented_functions=6086",
        "queue-probe.log": "Commentless functions: 27",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave895.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave895_queue_probe.log",
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
    require(quality["commentlessFunctionCount"] == 27, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6113, "quality TSV row count mismatch", failures)
    require(commented == 6086, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6086, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0059c610", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CFastVB__ReleaseOwnedObjectAndReset_Core", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173214599, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [PUBLIC_NOTE, FUNCTION_INDEX, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    owner_docs = {
        DXTEXTURE_DOC: ("Wave895", TAG, "0x0059b510 CDXTexture__ValidateJpegFrameAndBuildScanLayout", "0x0059be70 CDXTexture__AllocDecodeBlockAndLink", BACKUP_PATH),
        TEXTURE_DOC: ("Wave895", TAG, "0x0059b150 CTexture__InitDecodeLookupScratchTables", "0x0059b6f0 CTexture__BuildComponentPlaneLayoutTables", BACKUP_PATH),
        FASTVB_DOC: ("Wave895", TAG, "0x00598390 CFastVB__DetectCpuFeatureMask", "0x0059a71a CFastVB__SelectBestNodeTreeMatch", BACKUP_PATH),
    }
    for path, tokens in owner_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-decode-feature-tail-wave895") == r"py -3 tools\ghidra_decode_feature_tail_wave895_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave895 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20550 for row in attempts), "missing Wave895 attempt row", failures)


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
        print("Wave895 decode-feature-tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave895 decode-feature-tail probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
