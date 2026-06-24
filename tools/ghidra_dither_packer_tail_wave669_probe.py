#!/usr/bin/env python3
"""Validate Wave669 dither-packer tail read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave669-dither-packer-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_dither_packer_tail_wave669_2026-05-21.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
TEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "texture.cpp" / "_index.md"
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
    "dither-packer-tail-wave669",
    "wave669-readback-verified",
    "static-reaudit",
    "retail-binary-evidence",
    "signature-hardened",
    "comment-hardened",
}

PACKER_SIGNATURE = "void __thiscall {name}(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)"

TARGETS = {
    "0x00582ef8": {
        "name": "CDXTexture__PackTexels_Dither_Bits2_10_10_10",
        "tags": {"cdxtexture", "dither-packer", "bits2-10-10-10", "dword-output"},
        "comment_tokens": ("2-10-10-10-style", "+0x1058/+0x105c/+0x20", "10-bit scale"),
        "decompile": "00582ef8_CDXTexture__PackTexels_Dither_Bits2_10_10_10.c",
    },
    "0x00583041": {
        "name": "CDXTexture__PackTexels_Dither_Bits8888",
        "tags": {"cdxtexture", "dither-packer", "bits8888", "dword-output"},
        "comment_tokens": ("8-8-8-8-style", "four source vec4 lanes", "8-bit scale"),
        "decompile": "00583041_CDXTexture__PackTexels_Dither_Bits8888.c",
    },
    "0x0058318a": {
        "name": "CDXTexture__PackTexels_Dither_Bits888",
        "tags": {"cdxtexture", "dither-packer", "bits888", "dword-output"},
        "comment_tokens": ("24-bit 8-8-8-style", "three RGB source lanes", "32-bit store"),
        "decompile": "0058318a_CDXTexture__PackTexels_Dither_Bits888.c",
    },
    "0x005832af": {
        "name": "CDXTexture__PackTexels_Dither_Bits1616",
        "tags": {"cdxtexture", "dither-packer", "bits1616", "dword-output"},
        "comment_tokens": ("16-16-style", "first two source vec4 lanes", "16-bit scale"),
        "decompile": "005832af_CDXTexture__PackTexels_Dither_Bits1616.c",
    },
    "0x005833a6": {
        "name": "CDXTexture__PackTexels_Dither_Bits2_10_10_10_Alt",
        "tags": {"cdxtexture", "dither-packer", "bits2-10-10-10-alt", "dword-output"},
        "comment_tokens": ("alternate dithered 2-10-10-10-style", "source-lane order", "0x00582ef8"),
        "decompile": "005833a6_CDXTexture__PackTexels_Dither_Bits2_10_10_10_Alt.c",
    },
    "0x005834ef": {
        "name": "CDXTexture__PackTexels_Dither_Bits16_16_16_16",
        "tags": {"cdxtexture", "dither-packer", "bits16-16-16-16", "qword-output"},
        "comment_tokens": ("two 32-bit words per texel", "16-16-16-16-style", "sign-extension artifacts"),
        "decompile": "005834ef_CDXTexture__PackTexels_Dither_Bits16_16_16_16.c",
    },
    "0x00583670": {
        "name": "CDXTexture__PackTexels_Dither_PaletteIndexA8",
        "tags": {"cdxtexture", "dither-packer", "palette-index-a8", "word-output"},
        "comment_tokens": ("256-entry vec4 palette", "nearest RGB distance", "8-bit alpha companion"),
        "decompile": "00583670_CDXTexture__PackTexels_Dither_PaletteIndexA8.c",
    },
    "0x005837b7": {
        "name": "CDXTexture__PackTexels_Dither_PaletteIndex8",
        "tags": {"cdxtexture", "dither-packer", "palette-index8", "byte-output"},
        "comment_tokens": ("256-entry vec4 palette", "nearest RGBA distance", "8-bit palette index"),
        "decompile": "005837b7_CDXTexture__PackTexels_Dither_PaletteIndex8.c",
    },
    "0x00583891": {
        "name": "CFastVB__PackTexels_Dither_L8",
        "tags": {"cfastvb", "dither-packer", "l8", "byte-output", "luminance"},
        "comment_tokens": ("weighted RGB lanes", "0x005e72dc/0x005e72e0/0x005e72e4", "8-bit scale"),
        "decompile": "00583891_CFastVB__PackTexels_Dither_L8.c",
    },
    "0x00583979": {
        "name": "CFastVB__PackTexels_Dither_A8L8",
        "tags": {"cfastvb", "dither-packer", "a8l8", "word-output", "luminance"},
        "comment_tokens": ("A8L8-style", "alpha in the high byte", "luminance in the low byte"),
        "decompile": "00583979_CFastVB__PackTexels_Dither_A8L8.c",
    },
    "0x00583a94": {
        "name": "CTexture__PackTexels_Dither_A4L4",
        "tags": {"ctexture", "dither-packer", "a4l4", "byte-output", "luminance"},
        "comment_tokens": ("A4L4-style", "high nibble", "low nibble"),
        "decompile": "00583a94_CTexture__PackTexels_Dither_A4L4.c",
    },
    "0x00583ba4": {
        "name": "CTexture__PackTexels_Dither_L16",
        "tags": {"ctexture", "dither-packer", "l16", "word-output", "luminance"},
        "comment_tokens": ("16-bit output", "weighted RGB lanes", "16-bit scale"),
        "decompile": "00583ba4_CTexture__PackTexels_Dither_L16.c",
    },
}

for data in TARGETS.values():
    data["signature"] = PACKER_SIGNATURE.format(name=data["name"])

DOC_TOKENS = (
    "Wave669 dither packer tail",
    "dither-packer-tail-wave669",
    "0x00582ef8 CDXTexture__PackTexels_Dither_Bits2_10_10_10",
    "0x00583ba4 CTexture__PackTexels_Dither_L16",
    "0x00583c8e CTexture__PackTexels_Dither_Bits8_8",
)

OVERCLAIM_TOKENS = (
    "fully reverse-engineered",
    "runtime texture output proven",
    "exact dither table provenance proven",
    "exact texel-pack callback ABI proven",
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
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


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
        require("Wave669 static read-back" in comment, f"missing Wave669 comment at {address}", failures)
        require("Static metadata only" in comment, f"missing uncertainty clause at {address}", failures)
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


def check_logs(failures: list[str]) -> None:
    expected_exact = {
        "apply-wave669-dry.log": "SUMMARY: updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=12 missing=0 bad=0",
        "apply-wave669-apply.log": "SUMMARY: updated=12 skipped=0 renamed=0 would_rename=0 signature_updated=12 missing=0 bad=0",
        "apply-wave669-final-dry.log": "SUMMARY: updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=12 found=12 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "post-decompile.log": "targets=12 dumped=12 missing=0 failed=0",
        "post-instructions.log": "targets=12 missing=0",
        "post-xrefs.log": "Wrote 12 rows",
    }
    for filename, token in expected_exact.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"save report missing in {filename}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("ERROR REPORT SCRIPT ERROR" not in text, f"script error found in {filename}", failures)
        require("BAD:" not in text and "BADNAME:" not in text and "MISSING:" not in text, f"bad/missing marker found in {filename}", failures)

    instructions = read_text(BASE / "post-instructions.log")
    require("Wrote 444 instruction rows" in instructions, "instruction row count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require("test:ghidra-dither-packer-tail-wave669" in package.get("scripts", {}), "package script missing", failures)
    require((ROOT / "tools" / "ApplyDitherPackerTailWave669.java").is_file(), "apply script missing", failures)

    docs = (PUBLIC_NOTE, FUNCTION_INDEX, DXTEXTURE_DOC, FASTVB_DOC, TEXTURE_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG)
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text, f"{token!r} missing from {path.relative_to(ROOT)}", failures)
        for token in OVERCLAIM_TOKENS:
            require(token not in text, f"overclaim token {token!r} found in {path.relative_to(ROOT)}", failures)

    for path in (LEDGER, ATTEMPT_LOG):
        text = read_text(path)
        require("Wave669 dither packer tail" in text, f"Wave669 missing from {path.relative_to(ROOT)}", failures)
        require("dither-packer-tail-wave669" in text, f"Wave669 tag missing from {path.relative_to(ROOT)}", failures)


def check_state(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("diffCount") == 0, "backup diffCount mismatch", failures)
    require(backup.get("fileCount") == 19, "backup fileCount mismatch", failures)
    require(int(float(backup.get("byteCount", 0))) == 163810183, "backup byteCount mismatch", failures)
    require("post_wave669_dither_packer_tail_verified" in backup.get("backupPath", ""), "backup path mismatch", failures)

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6098, "queue total mismatch", failures)
    signals = queue.get("qualitySignals", {})
    require(signals.get("commentlessFunctionCount") == 2385, "queue commentless mismatch", failures)
    require(signals.get("undefinedSignatureCount") == 1217, "queue undefined-signature mismatch", failures)
    require(signals.get("paramSignatureCount") == 604, "queue param_N mismatch", failures)
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(head.get("address") == "0x00583c8e", f"queue head address mismatch: {head}", failures)
    require(head.get("name") == "CTexture__PackTexels_Dither_Bits8_8", f"queue head name mismatch: {head}", failures)

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(ledger[-1].get("task") == "Wave669 dither packer tail", "ledger last row mismatch", failures)
    require(attempts[-1].get("task") == "Wave669 dither packer tail", "attempt task mismatch", failures)
    require(attempts[-1].get("attempt_id") == 20324, "attempt id mismatch", failures)
    require(len(ledger) == 1065, "ledger row count mismatch", failures)
    require(len(attempts) == 20325, "attempt row count mismatch", failures)

    tracking = read_json(TRACKING)
    counters = tracking.get("counters", {})
    require(tracking.get("current_focus", "").startswith("Wave669 dither packer tail"), "tracking current_focus mismatch", failures)
    require(counters.get("ledger_rows") == 1065, "tracking ledger_rows mismatch", failures)
    require(counters.get("attempt_rows") == 20325, "tracking attempt_rows mismatch", failures)
    require(counters.get("completed") == 1056, "tracking completed mismatch", failures)
    require(counters.get("pending") == 9, "tracking pending mismatch", failures)
    require(tracking.get("next_attempt_id") == 20325, "tracking next_attempt_id mismatch", failures)

    for path in (DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        require("Wave669 dither packer tail" in text, f"Wave669 missing from {path.name}", failures)
        require("dither-packer-tail-wave669" in text, f"Wave669 tag missing from {path.name}", failures)


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
    print("Ghidra dither packer tail Wave669 probe")
    print(f"Status: {status}")
    print(f"Targets: {len(TARGETS)}")
    print(f"Evidence root: {BASE.relative_to(ROOT)}")
    if failures:
        for failure in failures:
            print(f"- {failure}")
    return 1 if failures and args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
