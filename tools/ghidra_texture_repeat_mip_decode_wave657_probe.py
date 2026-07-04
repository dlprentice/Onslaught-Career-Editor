#!/usr/bin/env python3
"""Validate Wave657 texture repeat/mip/decode read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave657-texture-repeat-mip-decode"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_texture_repeat_mip_decode_wave657_2026-05-20.md"
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
BACKUP_SUMMARY = BASE / "backup-summary.json"

COMMON_TAGS = {
    "static-reaudit",
    "texture-repeat-mip-decode-wave657",
    "retail-binary-evidence",
    "signature-hardened",
    "comment-hardened",
}

TARGETS = {
    "0x00574abb": {
        "name": "CDXTexture__RepeatCallbackN",
        "signature": "void __stdcall CDXTexture__RepeatCallbackN(int unused_arg0, int unused_arg1, int repeat_count, void * callback_fn)",
        "tags": {"cdxtexture", "callback-repeat", "unused-args", "retained-name"},
        "comment_tokens": ("callback_fn", "repeat_count", "owner label provenance"),
        "decompile": "00574abb_CDXTexture__RepeatCallbackN.c",
    },
    "0x00574e2b": {
        "name": "CDXTexture__GenerateMipChainBySurfaceCopy",
        "signature": "uint __stdcall CDXTexture__GenerateMipChainBySurfaceCopy(void * surface_chain, int unused_context, uint start_level, uint mip_flags)",
        "tags": {"cdxtexture", "mip-chain", "surface-copy", "d3d-status", "vtable-surface"},
        "comment_tokens": ("vfunc +0x28", "vfunc +0x34/+0x48", "runtime mip output"),
        "decompile": "00574e2b_CDXTexture__GenerateMipChainBySurfaceCopy.c",
    },
    "0x00575923": {
        "name": "CDXTexture__DecodeMappedFileToTexture",
        "signature": "int __stdcall CDXTexture__DecodeMappedFileToTexture(void * decode_target, void * mapped_filename)",
        "tags": {"cdxtexture", "mapped-file-decode", "read-only-open", "implicit-register-state"},
        "comment_tokens": ("mapped-file context", "read-only", "implicit ESI/EAX/EDX state"),
        "decompile": "00575923_CDXTexture__DecodeMappedFileToTexture.c",
    },
}

DOC_TOKENS = (
    "Wave657 texture repeat/mip/decode hardening",
    "3583",
    "2510",
    "725",
    "0x00575986 Math__IsFloatDiffOutsideTolerance",
    "[maintainer-local-ghidra-backup-root]\\BEA_20260520-212214_post_wave657_texture_repeat_mip_decode_verified",
)

OVERCLAIM_TOKENS = (
    "runtime texture conversion behavior proven",
    "runtime mip output proven",
    "exact D3D interface/type enum proven",
    "exact callback ABI proven",
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
        require("Wave657 texture repeat/mip/decode hardening" in comment, f"missing Wave657 comment at {address}", failures)
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

    require(sum(1 for _ in (BASE / "post-xrefs.tsv").open(encoding="utf-8-sig")) == 5, "post-xrefs.tsv should have 5 lines", failures)
    require(sum(1 for _ in (BASE / "post-instructions.tsv").open(encoding="utf-8-sig")) == 724, "post-instructions.tsv should have 724 lines", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-wave657-dry.log": "SUMMARY: updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=3 missing=0 bad=0",
        "apply-wave657-apply.log": "SUMMARY: updated=3 skipped=0 renamed=0 would_rename=0 signature_updated=3 missing=0 bad=0",
        "apply-wave657-final-dry.log": "SUMMARY: updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "export-post-metadata-relative.log": "targets=3 found=3 missing=0",
        "export-post-tags-relative.log": "ExportFunctionTagsByAddress complete: rows=3 missing=0",
        "export-post-xrefs-relative.log": "Wrote 4 rows to:",
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
    require("test:ghidra-texture-repeat-mip-decode-wave657" in package.get("scripts", {}), "package script missing", failures)

    for path in (PUBLIC_NOTE, FUNCTION_INDEX, DXTEXTURE_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG):
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text, f"{token!r} missing from {path.relative_to(ROOT)}", failures)
        for token in OVERCLAIM_TOKENS:
            require(token not in text, f"overclaim token {token!r} found in {path.relative_to(ROOT)}", failures)

    for path in (LEDGER, ATTEMPT_LOG):
        text = read_text(path)
        require("Wave657 texture repeat/mip/decode hardening" in text, f"Wave657 missing from {path.relative_to(ROOT)}", failures)
        require("texture-repeat-mip-decode-wave657" in text, f"Wave657 tag missing from {path.relative_to(ROOT)}", failures)


def check_state(failures: list[str]) -> None:
    tracking = read_json(TRACKING)
    require(tracking.get("next_attempt_id") == 20313, "tracking next_attempt_id mismatch", failures)
    require(tracking.get("current_focus", "").startswith("Wave657 texture repeat/mip/decode hardening"), "tracking current_focus mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("diffCount") == 0, "backup diffCount mismatch", failures)
    require(backup.get("fileCount") == 19, "backup fileCount mismatch", failures)
    require(int(backup.get("byteCount", 0)) == 163253127, "backup byteCount mismatch", failures)
    require(backup.get("backupPath") == "[maintainer-local-ghidra-backup-root]\\BEA_20260520-212214_post_wave657_texture_repeat_mip_decode_verified", "backup path mismatch", failures)

    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue.get("totalFunctions") == 6093, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 2510, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 1217, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 725, "queue param mismatch", failures)
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(head.get("address") == "0x00575986", "queue head address mismatch", failures)
    require(head.get("name") == "Math__IsFloatDiffOutsideTolerance", "queue head name mismatch", failures)

    ledger_last = read_jsonl(LEDGER)[-1]
    attempt_last = read_jsonl(ATTEMPT_LOG)[-1]
    require(ledger_last.get("task") == "Wave657 texture repeat/mip/decode hardening", "ledger last row mismatch", failures)
    require(attempt_last.get("attempt_id") == 20312, "attempt id mismatch", failures)
    require(attempt_last.get("task") == "Wave657 texture repeat/mip/decode hardening", "attempt task mismatch", failures)

    for path in (DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        require("Wave657 texture repeat/mip/decode hardening" in text, f"Wave657 missing from {path.name}", failures)
        require("0x00575986 Math__IsFloatDiffOutsideTolerance" in text, f"next queue head missing from {path.name}", failures)


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
    print("Ghidra texture repeat/mip/decode Wave657 probe")
    print(f"Status: {status}")
    print(f"Targets: {len(TARGETS)}")
    print(f"Evidence root: {BASE.relative_to(ROOT)}")
    if failures:
        for failure in failures:
            print(f"- {failure}")
    return 1 if failures and args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
