#!/usr/bin/env python3
"""Validate Wave656 texture format/upload read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave656-texture-format-upload"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_texture_format_upload_wave656_2026-05-20.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
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
BACKUP_SUMMARY = BASE / "backup-summary.json"

COMMON_TAGS = {
    "static-reaudit",
    "texture-format-upload-wave656",
    "retail-binary-evidence",
    "signature-hardened",
    "comment-hardened",
}

TARGETS = {
    "0x00574270": {
        "name": "CDXTexture__FindFormatDescriptorById",
        "signature": "int * __stdcall CDXTexture__FindFormatDescriptorById(int format_id)",
        "tags": {"cdxtexture", "format-descriptor", "descriptor-table"},
        "comment_tokens": ("9-dword rows", "DAT_005e6a40", "runtime texture behavior"),
        "decompile": "00574270_CDXTexture__FindFormatDescriptorById.c",
    },
    "0x00574296": {
        "name": "CFastVB__ComputeFormatMatchPenalty",
        "signature": "uint __fastcall CFastVB__ComputeFormatMatchPenalty(void * requested_descriptor, void * candidate_descriptor)",
        "tags": {"cfastvb", "format-scoring", "compatibility-matrix"},
        "comment_tokens": ("DAT_005e7270", "weighted field-difference penalties", "descriptor schema"),
        "decompile": "00574296_CFastVB__ComputeFormatMatchPenalty.c",
    },
    "0x0057430b": {
        "name": "CDXTexture__SelectBestCompatibleFormat",
        "signature": "int __stdcall CDXTexture__SelectBestCompatibleFormat(void * format_id_list, int allow_mode_one_descriptor, void * requested_descriptor)",
        "tags": {"cdxtexture", "format-selection", "descriptor-penalty", "zero-terminated-list"},
        "comment_tokens": ("zero-terminated format-id list", "tie-breaks", "runtime device compatibility"),
        "decompile": "0057430b_CDXTexture__SelectBestCompatibleFormat.c",
    },
    "0x0057437a": {
        "name": "CFastVB__SelectBestFormatHandler",
        "signature": "int __stdcall CFastVB__SelectBestFormatHandler(void * device_or_null, uint usage_flags, int resource_type, void * requested_descriptor)",
        "tags": {"cfastvb", "format-handler", "d3d-probe", "debug-mute", "format-selection"},
        "comment_tokens": ("mutes D3D debug output", "device-like vtable", "runtime format behavior"),
        "decompile": "0057437a_CFastVB__SelectBestFormatHandler.c",
    },
    "0x00574476": {
        "name": "CDXTexture__MapFormatTokenToInternalCode",
        "signature": "int __stdcall CDXTexture__MapFormatTokenToInternalCode(int format_token)",
        "tags": {"cdxtexture", "format-token", "fourcc-map"},
        "comment_tokens": ("AL16", "R16", "texture-format taxonomy"),
        "decompile": "00574476_CDXTexture__MapFormatTokenToInternalCode.c",
    },
    "0x00574577": {
        "name": "CFastVB__ReturnInputInt",
        "signature": "int __fastcall CFastVB__ReturnInputInt(int value)",
        "tags": {"cfastvb", "identity-callback", "retained-name"},
        "comment_tokens": ("retained-name", "identity helper", "profile/conversion tables"),
        "decompile": "00574577_CFastVB__ReturnInputInt.c",
    },
    "0x0057457a": {
        "name": "CDXTexture__LoadAndUploadMappedTexture_0057457a",
        "signature": "int __stdcall CDXTexture__LoadAndUploadMappedTexture_0057457a(void * target_ref, void * mode_flags, void * surface_ref, void * context_ref, void * fallback_ref)",
        "tags": {"cdxtexture", "mapped-texture-upload", "implicit-register-state", "surface-tree", "address-suffixed-helper"},
        "comment_tokens": ("D3D-style status codes", "implicit EAX/ESI state", "runtime upload behavior"),
        "decompile": "0057457a_CDXTexture__LoadAndUploadMappedTexture_0057457a.c",
    },
    "0x00574645": {
        "name": "Platform__LoadAndUploadMappedTextureWrapper",
        "signature": "void __stdcall Platform__LoadAndUploadMappedTextureWrapper(void * target_ref, void * mode_flags, void * unused_surface_ref, void * context_ref, void * fallback_ref)",
        "tags": {"platform-wrapper", "screen-dump", "mapped-texture-upload", "ignored-arg"},
        "comment_tokens": ("third stack argument unused", "screen-dump", "wrapper ABI"),
        "decompile": "00574645_Platform__LoadAndUploadMappedTextureWrapper.c",
    },
}

DOC_TOKENS = (
    "Wave656 texture format/upload hardening",
    "3580",
    "2513",
    "728",
    "0x00574abb CDXTexture__RepeatCallbackN",
    "G:\\GhidraBackups\\BEA_20260520-205422_post_wave656_texture_format_upload_verified",
)

OVERCLAIM_TOKENS = (
    "runtime format selection proven",
    "runtime upload behavior proven",
    "exact texture descriptor schema proven",
    "exact device interface proven",
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
        require("Wave656 texture format/upload hardening" in comment, f"missing Wave656 comment at {address}", failures)
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

    require(sum(1 for _ in (BASE / "post-xrefs.tsv").open(encoding="utf-8-sig")) == 50, "post-xrefs.tsv should have 50 lines", failures)
    require(sum(1 for _ in (BASE / "post-instructions.tsv").open(encoding="utf-8-sig")) == 1769, "post-instructions.tsv should have 1769 lines", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-wave656-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=8 missing=0 bad=0",
        "apply-wave656-apply.log": "SUMMARY: updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=8 missing=0 bad=0",
        "apply-wave656-final-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "export-post-metadata-relative.log": "targets=8 found=8 missing=0",
        "export-post-tags-relative.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "export-post-xrefs-relative.log": "Wrote 49 rows to:",
        "export-post-instructions-relative.log": "targets=8 missing=0",
        "export-decompile-post-relative.log": "targets=8 dumped=8 missing=0 failed=0",
    }
    for filename, token in expected.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("BAD:" not in text and "MISSING:" not in text, f"bad/missing marker found in {filename}", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require("test:ghidra-texture-format-upload-wave656" in package.get("scripts", {}), "package script missing", failures)

    for path in (PUBLIC_NOTE, FUNCTION_INDEX, DXTEXTURE_DOC, FASTVB_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG):
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text, f"{token!r} missing from {path.relative_to(ROOT)}", failures)
        for token in OVERCLAIM_TOKENS:
            require(token not in text, f"overclaim token {token!r} found in {path.relative_to(ROOT)}", failures)

    for path in (LEDGER, ATTEMPT_LOG):
        text = read_text(path)
        require("Wave656 texture format/upload hardening" in text, f"Wave656 missing from {path.relative_to(ROOT)}", failures)
        require("texture-format-upload-wave656" in text, f"Wave656 tag missing from {path.relative_to(ROOT)}", failures)


def check_state(failures: list[str]) -> None:
    tracking = read_json(TRACKING)
    require(tracking.get("next_attempt_id") == 20312, "tracking next_attempt_id mismatch", failures)
    require(tracking.get("current_focus", "").startswith("Wave656 texture format/upload hardening"), "tracking current_focus mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("diffCount") == 0, "backup diffCount mismatch", failures)
    require(backup.get("fileCount") == 19, "backup fileCount mismatch", failures)
    require(int(backup.get("byteCount", 0)) == 163220359, "backup byteCount mismatch", failures)
    require(backup.get("backupPath") == "G:\\GhidraBackups\\BEA_20260520-205422_post_wave656_texture_format_upload_verified", "backup path mismatch", failures)

    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue.get("totalFunctions") == 6093, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 2513, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 1217, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 728, "queue param mismatch", failures)
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(head.get("address") == "0x00574abb", "queue head address mismatch", failures)
    require(head.get("name") == "CDXTexture__RepeatCallbackN", "queue head name mismatch", failures)

    ledger_last = read_jsonl(LEDGER)[-1]
    attempt_last = read_jsonl(ATTEMPT_LOG)[-1]
    require(ledger_last.get("task") == "Wave656 texture format/upload hardening", "ledger last row mismatch", failures)
    require(attempt_last.get("attempt_id") == 20311, "attempt id mismatch", failures)
    require(attempt_last.get("task") == "Wave656 texture format/upload hardening", "attempt task mismatch", failures)

    for path in (DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        require("Wave656 texture format/upload hardening" in text, f"Wave656 missing from {path.name}", failures)
        require("0x00574abb CDXTexture__RepeatCallbackN" in text, f"next queue head missing from {path.name}", failures)


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
    print("Ghidra texture format/upload Wave656 probe")
    print(f"Status: {status}")
    print(f"Targets: {len(TARGETS)}")
    print(f"Evidence root: {BASE.relative_to(ROOT)}")
    if failures:
        for failure in failures:
            print(f"- {failure}")
    return 1 if failures and args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
