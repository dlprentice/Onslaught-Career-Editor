#!/usr/bin/env python3
"""Validate Wave842 CVBufTexture render-restore read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave842-cvbuftexture-render-restore"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cvbuftexture_render_restore_wave842_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
VBUFTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "vbuftexture.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

ADDRESS = "0x0050ab60"
NAME = "CVBufTexture__RenderAndRestoreStateFlag4"
SIGNATURE = "void __stdcall CVBufTexture__RenderAndRestoreStateFlag4(void * dynamic_context, int unused_zero_arg, int enable_dynamic_flag_source)"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260525-035851_post_wave842_cvbuftexture_render_restore_verified"
NEXT_HEAD = "0x0050b030 OID__TraceLineAndSelectBestTargetHit"

EXPECTED_TAGS = {
    "static-reaudit",
    "cvbuftexture-render-restore-wave842",
    "wave842-readback-verified",
    "retail-binary-evidence",
    "signature-hardened",
    "comment-hardened",
    "cvbuftexture",
    "render-state",
    "dynamic-unit-render",
    "stdcall-ret0c",
}

CORE_DOC_TOKENS = (
    "Wave842 CVBufTexture render restore",
    "cvbuftexture-render-restore-wave842",
    "0x0050ab60 CVBufTexture__RenderAndRestoreStateFlag4",
    SIGNATURE,
    "0x0053e77d CDXEngine__Render",
    "DAT_009c7c56",
    "DAT_0089ce54 bit 4",
    "CVBufTexture__SetStateCacheModeByFlag(1)",
    "CVBufTexture__RenderDynamicUnitPass",
    "5666/6098 = 92.92%",
    NEXT_HEAD,
    BACKUP_PATH,
)

COMMENT_TOKENS = (
    "Wave842 static read-back/signature/comment hardening",
    "CDXEngine__Render callsite 0x0053e77d",
    "[EBP+0x470]",
    "DAT_009c7c56",
    "RET 0xc",
    "DAT_0089ce54 bit 4",
    "CVBufTexture__RenderDynamicUnitPass",
    "CVBufTexture__SetStateCacheModeByFlag(1)",
    "runtime rendering behavior",
)

OVERCLAIM_TOKENS = (
    "runtime rendering behavior proven",
    "exact source function identity proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 1,
        "pre-tags.tsv": 1,
        "pre-xrefs.tsv": 1,
        "pre-instructions.tsv": 261,
        "pre-target-deep-instructions.tsv": 521,
        "pre-xref-site-instructions.tsv": 71,
        "pre-decompile/index.tsv": 1,
        "pre-context-metadata.tsv": 10,
        "pre-context-tags.tsv": 10,
        "pre-context-decompile/index.tsv": 10,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 1,
        "post-instructions.tsv": 261,
        "post-target-deep-instructions.tsv": 521,
        "post-xref-site-instructions.tsv": 71,
        "post-decompile/index.tsv": 1,
        "post-context-metadata.tsv": 10,
        "post-context-tags.tsv": 10,
        "post-context-decompile/index.tsv": 10,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = read_tsv(BASE / "post-metadata.tsv")[0]
    require(normalize_address(metadata["address"]) == ADDRESS, "metadata address mismatch", failures)
    require(metadata["name"] == NAME, "metadata name mismatch", failures)
    require(metadata["signature"] == SIGNATURE, f"metadata signature mismatch: {metadata['signature']}", failures)
    require(metadata["status"] == "OK", "metadata status mismatch", failures)
    for token in COMMENT_TOKENS:
        require(token in metadata.get("comment", ""), f"missing comment token: {token}", failures)

    tags = set(read_tsv(BASE / "post-tags.tsv")[0]["tags"].split(";"))
    require(EXPECTED_TAGS.issubset(tags), f"missing tags: {EXPECTED_TAGS - tags}", failures)

    xref = read_tsv(BASE / "post-xrefs.tsv")[0]
    require(normalize_address(xref["target_addr"]) == ADDRESS, "xref target mismatch", failures)
    require(normalize_address(xref["from_addr"]) == "0x0053e77d", "xref caller mismatch", failures)
    require(xref["from_function"] == "CDXEngine__Render", "xref caller function mismatch", failures)
    require(xref["ref_type"] == "UNCONDITIONAL_CALL", "xref type mismatch", failures)

    instructions = read_tsv(BASE / "post-instructions.tsv")
    instruction_text = "\n".join(f"{row.get('mnemonic')} {row.get('operands')}" for row in instructions)
    for token in ("PUSH 0x1", "CALL 0x0053f040", "TEST byte ptr [0x0089ce54], 0x4", "CALL 0x0044a690", "CALL 0x00476fe0", "RET 0xc"):
        require(token in instruction_text, f"missing instruction token: {token}", failures)

    caller_text = "\n".join(f"{row.get('mnemonic')} {row.get('operands')}" for row in read_tsv(BASE / "post-xref-site-instructions.tsv"))
    for token in ("MOV ECX, dword ptr [EBP + 0x470]", "MOV AL, [0x009c7c56]", "PUSH EAX", "PUSH EBX", "CALL 0x0050ab60"):
        require(token in caller_text, f"missing caller token: {token}", failures)

    decompile_index = read_tsv(BASE / "post-decompile" / "index.tsv")[0]
    require(decompile_index["signature"] == SIGNATURE, "decompile signature mismatch", failures)
    require(decompile_index["status"] == "OK", "decompile status mismatch", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 1 rows",
        "post-instructions.log": "Wrote 261 instruction rows",
        "post-target-deep-instructions.log": "Wrote 521 instruction rows",
        "post-xref-site-instructions.log": "Wrote 71 instruction rows",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "post-context-metadata.log": "targets=10 found=10 missing=0",
        "post-context-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "post-context-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "READBACK_BAD", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    quality_log = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave842.log")
    queue_log = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave842_queue_probe.log")
    require("total_functions=6098 commented_functions=5666" in quality_log, "quality refresh count mismatch", failures)
    require("Commentless functions: 432" in queue_log, "queue probe count mismatch", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 432, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict = signature_counts(rows)
    raw = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5666, "quality TSV commented count mismatch", failures)
    require(strict == 5666, "quality TSV strict count mismatch", failures)
    require(raw is not None and raw.get("address") == "0x0050b030", "raw head address mismatch", failures)
    require(raw is not None and raw.get("name") == "OID__TraceLineAndSelectBestTargetHit", "raw head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171838343 or backup.get("totalBytes") == 171838343.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        VBUFTEXTURE_DOC,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in CORE_DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    expected_script = r"py -3 tools\ghidra_cvbuftexture_render_restore_wave842_probe.py --check"
    require(package.get("scripts", {}).get("test:ghidra-cvbuftexture-render-restore-wave842") == expected_script, "missing package script", failures)
    require(any(row.get("task") == "Wave842 CVBufTexture render restore" for row in read_jsonl(LEDGER)), "missing Wave842 ledger row", failures)
    require(any(row.get("task") == "Wave842 CVBufTexture render restore" and row.get("attempt_id") == 20497 for row in read_jsonl(ATTEMPT_LOG)), "missing Wave842 attempt row", failures)


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
        print("Wave842 CVBufTexture render-restore probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave842 CVBufTexture render-restore probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
