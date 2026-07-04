#!/usr/bin/env python3
"""Validate Wave896 decode-cleanup read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave896-decode-cleanup-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_decode_cleanup_tail_wave896_2026-05-26.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260526-071320_post_wave896_decode_cleanup_tail_verified"
COMMON_TAGS = {
    "static-reaudit",
    "decode-cleanup-tail-wave896",
    "wave896-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-verified",
    "important-texture-decode-infrastructure",
    "raw-commentless-tail",
    "cleanup-helper",
}
TARGETS = {
    "0x0059c610": {
        "name": "CFastVB__ReleaseOwnedObjectAndReset_Core",
        "signature": "void __stdcall CFastVB__ReleaseOwnedObjectAndReset_Core(void * decode_state_header)",
        "tokens": ("Wave896 static read-back", "0x00591050", "0x00592b0c", "vfunc +0x28", "+0x04", "+0x14"),
        "xrefs": {"0x00591050", "0x00592b0c"},
        "extra_tags": {"owned-object-release-reset", "parser-context-cleanup", "vtable-callback"},
    },
    "0x0059ccb3": {
        "name": "CDXTexture__FreeDecodeStateIfOwnerPresent",
        "signature": "void __stdcall CDXTexture__FreeDecodeStateIfOwnerPresent(void * decode_state, void * decode_buffer)",
        "tokens": ("Wave896 static read-back", "0x00592ded", "0x00593442", "0x0059517e", "CRT__FreeBase", "RET 0x8"),
        "xrefs": {"0x00592ded", "0x00593442", "0x0059517e"},
        "extra_tags": {"png-decode-cleanup", "decode-buffer-free", "crt-freebase-gate"},
    },
}
CORE_ANCHORS = (
    "Wave896 decode cleanup tail",
    "decode-cleanup-tail-wave896",
    "0x0059c610 CFastVB__ReleaseOwnedObjectAndReset_Core",
    "0x0059ccb3 CDXTexture__FreeDecodeStateIfOwnerPresent",
    "0x005a09f8 CFastVB__ConvertHalfToFloat8_SIMDKernel",
    "6088/6113 = 99.59%",
    BACKUP_PATH,
)
OVERCLAIM_TOKENS = (
    "runtime cleanup behavior proven",
    "runtime image decode cleanup behavior proven",
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
        "pre-metadata.tsv": 2,
        "pre-tags.tsv": 2,
        "pre-xrefs.tsv": 13,
        "pre-instructions.tsv": 22,
        "pre-decompile/index.tsv": 2,
        "post-metadata.tsv": 2,
        "post-tags.tsv": 2,
        "post-xrefs.tsv": 13,
        "post-instructions.tsv": 22,
        "post-decompile/index.tsv": 2,
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
            comment = row.get("comment", "")
            for token in expected["tokens"]:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

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
        "apply-dry.log": "SUMMARY: updated=0 skipped=2 renamed=0 would_rename=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=2 skipped=0 renamed=0 would_rename=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=2 renamed=0 would_rename=0 missing=0 bad=0",
        "post-metadata.log": "targets=2 found=2 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=2 missing=0",
        "post-xrefs.log": "Wrote 13 rows",
        "post-instructions.log": "Wrote 22 function-body instruction rows",
        "post-decompile.log": "targets=2 dumped=2 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6113 commented_functions=6088",
        "queue-probe.log": "Commentless functions: 25",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave896.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave896_queue_probe.log",
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
    require(quality["commentlessFunctionCount"] == 25, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6113, "quality TSV row count mismatch", failures)
    require(commented == 6088, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6088, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x005a09f8", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CFastVB__ConvertHalfToFloat8_SIMDKernel", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 173214599, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    for path in (PUBLIC_NOTE, FUNCTION_INDEX, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG, FASTVB_DOC, DXTEXTURE_DOC, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-decode-cleanup-tail-wave896") == r"py -3 tools\ghidra_decode_cleanup_tail_wave896_probe.py --check",
        "missing package script",
        failures,
    )
    require(any(row.get("task") == "Wave896 decode cleanup tail" for row in read_jsonl(LEDGER)), "missing Wave896 ledger row", failures)
    require(any(row.get("task") == "Wave896 decode cleanup tail" and row.get("attempt_id") == 20551 for row in read_jsonl(ATTEMPT_LOG)), "missing Wave896 attempt row", failures)


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
        print("Wave896 decode-cleanup probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave896 decode-cleanup probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
