#!/usr/bin/env python3
"""Validate Wave670 texel-packer continuation read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave670-texel-packer-continuation"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_texel_packer_continuation_wave670_2026-05-21.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
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
    "static-reaudit",
    "texel-packer-continuation-wave670",
    "wave670-readback-verified",
    "retail-binary-evidence",
    "signature-hardened",
    "comment-hardened",
    "texel-packer",
}

PACKER_SIGNATURE = (
    "void __thiscall {name}(void * this, uint output_x, uint output_y, "
    "float * source_vec4_array, int unused_context)"
)

TARGETS = {
    "0x00583c8e": {
        "name": "CTexture__PackTexels_Dither_Bits8_8",
        "tags": {"ctexture", "dither-packer", "bits8-8", "word-output"},
        "comment_tokens": ("8-8-style", "+0x1058/+0x105c/+0x20", "+0x1060", "+0x34"),
        "decompile": "00583c8e_CTexture__PackTexels_Dither_Bits8_8.c",
    },
    "0x00583d89": {
        "name": "CTexture__PackTexels_Dither_Bits5_5_5",
        "tags": {"ctexture", "dither-packer", "bits5-5-5", "word-output"},
        "comment_tokens": ("5-5-5-style", "shared output pointer", "dither-table gates"),
        "decompile": "00583d89_CTexture__PackTexels_Dither_Bits5_5_5.c",
    },
    "0x00583eb3": {
        "name": "CTexture__PackTexels_Dither_Bits8_8_8_Alt",
        "tags": {"ctexture", "dither-packer", "bits8-8-8-alt", "dword-output"},
        "comment_tokens": ("alternate dithered 8-8-8-style", "32-bit store", "lane order"),
        "decompile": "00583eb3_CTexture__PackTexels_Dither_Bits8_8_8_Alt.c",
    },
    "0x00583fe5": {
        "name": "CTexture__PackTexels_Dither_Bits8_8_8_8_Alt",
        "tags": {"ctexture", "dither-packer", "bits8-8-8-8-alt", "dword-output"},
        "comment_tokens": ("alternate dithered 8-8-8-8-style", "four rounded source lanes", "dither-table gates"),
        "decompile": "00583fe5_CTexture__PackTexels_Dither_Bits8_8_8_8_Alt.c",
    },
    "0x00584144": {
        "name": "CFastVB__PackTexels_NoDither_Bits16_16",
        "tags": {"cfastvb", "no-dither-named", "dither-term-observed", "bits16-16", "dword-output"},
        "comment_tokens": ("currently named no-dither 16-16", "shared dither-table term at +0x34", "32-bit texel"),
        "decompile": "00584144_CFastVB__PackTexels_NoDither_Bits16_16.c",
    },
    "0x0058423f": {
        "name": "CFastVB__PackTexels_NoDither_Bits2_10_10_10",
        "tags": {"cfastvb", "no-dither-named", "dither-term-observed", "bits2-10-10-10", "dword-output"},
        "comment_tokens": ("currently named no-dither 2-10-10-10", "shared dither-table term at +0x34", "four rounded source lanes"),
        "decompile": "0058423f_CFastVB__PackTexels_NoDither_Bits2_10_10_10.c",
    },
    "0x0058439e": {
        "name": "CFastVB__PackTexels_NoDither_Bits16_16_16_16",
        "tags": {"cfastvb", "no-dither-named", "dither-term-observed", "bits16-16-16-16", "qword-output"},
        "comment_tokens": ("currently named no-dither 16-16-16-16", "two 32-bit words", "shared dither-table term at +0x34"),
        "decompile": "0058439e_CFastVB__PackTexels_NoDither_Bits16_16_16_16.c",
    },
    "0x00584535": {
        "name": "CTexture__PackTexels_Dither_Bits8_8_FromAuxLookup",
        "tags": {"ctexture", "dither-packer", "bits8-8-from-aux-lookup", "word-output", "indirect-helper"},
        "comment_tokens": ("observed indirect helper 0x00575d99", "two local float lanes", "16-bit texel"),
        "decompile": "00584535_CTexture__PackTexels_Dither_Bits8_8_FromAuxLookup.c",
    },
    "0x0058463a": {
        "name": "CTexture__PackTexels_Dither_L16_Alt",
        "tags": {"ctexture", "dither-packer", "l16-alt", "word-output", "luminance"},
        "comment_tokens": ("alternate dithered luminance", "0x005e72dc/0x005e72e0/0x005e72e4", "16-bit scale"),
        "decompile": "0058463a_CTexture__PackTexels_Dither_L16_Alt.c",
    },
}

for data in TARGETS.values():
    data["signature"] = PACKER_SIGNATURE.format(name=data["name"])

DOC_TOKENS = (
    "Wave670 texel packer continuation",
    "texel-packer-continuation-wave670",
    "0x00583c8e CTexture__PackTexels_Dither_Bits8_8",
    "0x0058463a CTexture__PackTexels_Dither_L16_Alt",
    "0x00584724 CDXTexture__PackTexels_CallbackPerTexel_RepeatA",
)

OVERCLAIM_TOKENS = (
    "fully reverse-engineered",
    "runtime texture output proven",
    "exact dither table provenance proven",
    "exact texel-pack callback ABI proven",
    "exact no-dither naming rationale proven",
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
        require("Wave670 static read-back" in comment, f"missing Wave670 comment at {address}", failures)
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
        "apply-wave670-dry.log": "SUMMARY: updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=9 missing=0 bad=0",
        "apply-wave670-apply.log": "SUMMARY: updated=9 skipped=0 renamed=0 would_rename=0 signature_updated=9 missing=0 bad=0",
        "apply-wave670-final-dry.log": "SUMMARY: updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=9 found=9 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=9 missing=0",
        "post-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
        "post-instructions.log": "targets=9 missing=0",
        "post-xrefs.log": "Wrote 9 rows",
    }
    for filename, token in expected_exact.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"save report missing in {filename}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("ERROR REPORT SCRIPT ERROR" not in text, f"script error found in {filename}", failures)
        require("BAD:" not in text and "BADNAME:" not in text and "MISSING:" not in text, f"bad/missing marker found in {filename}", failures)

    instructions = read_text(BASE / "post-instructions.log")
    require("Wrote 729 instruction rows" in instructions, "instruction row count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require("test:ghidra-texel-packer-continuation-wave670" in package.get("scripts", {}), "package script missing", failures)
    require((ROOT / "tools" / "ApplyTexelPackerContinuationWave670.java").is_file(), "apply script missing", failures)

    docs = (PUBLIC_NOTE, FUNCTION_INDEX, FASTVB_DOC, TEXTURE_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG)
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text, f"{token!r} missing from {path.relative_to(ROOT)}", failures)
        for token in OVERCLAIM_TOKENS:
            require(token not in text, f"overclaim token {token!r} found in {path.relative_to(ROOT)}", failures)

    for path in (LEDGER, ATTEMPT_LOG):
        text = read_text(path)
        require("Wave670 texel packer continuation" in text, f"Wave670 missing from {path.relative_to(ROOT)}", failures)
        require("texel-packer-continuation-wave670" in text, f"Wave670 tag missing from {path.relative_to(ROOT)}", failures)


def check_state(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("diffCount") == 0, "backup diffCount mismatch", failures)
    require(backup.get("fileCount") == 19, "backup fileCount mismatch", failures)
    require(int(float(backup.get("byteCount", 0))) == 163842951, "backup byteCount mismatch", failures)
    require("post_wave670_texel_packer_continuation_verified" in backup.get("backupPath", ""), "backup path mismatch", failures)

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6098, "queue total mismatch", failures)
    signals = queue.get("qualitySignals", {})
    require(signals.get("commentlessFunctionCount") == 2376, "queue commentless mismatch", failures)
    require(signals.get("undefinedSignatureCount") == 1217, "queue undefined-signature mismatch", failures)
    require(signals.get("paramSignatureCount") == 595, "queue param_N mismatch", failures)
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(head.get("address") == "0x00584724", f"queue head address mismatch: {head}", failures)
    require(head.get("name") == "CDXTexture__PackTexels_CallbackPerTexel_RepeatA", f"queue head name mismatch: {head}", failures)

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(ledger[-1].get("task") == "Wave670 texel packer continuation", "ledger last row mismatch", failures)
    require(attempts[-1].get("task") == "Wave670 texel packer continuation", "attempt task mismatch", failures)
    require(attempts[-1].get("attempt_id") == 20325, "attempt id mismatch", failures)
    require(len(ledger) == 1066, "ledger row count mismatch", failures)
    require(len(attempts) == 20326, "attempt row count mismatch", failures)

    tracking = read_json(TRACKING)
    counters = tracking.get("counters", {})
    require(tracking.get("current_focus", "").startswith("Wave670 texel packer continuation"), "tracking current_focus mismatch", failures)
    require(counters.get("ledger_rows") == 1066, "tracking ledger_rows mismatch", failures)
    require(counters.get("attempt_rows") == 20326, "tracking attempt_rows mismatch", failures)
    require(counters.get("completed") == 1057, "tracking completed mismatch", failures)
    require(counters.get("pending") == 9, "tracking pending mismatch", failures)
    require(tracking.get("next_attempt_id") == 20326, "tracking next_attempt_id mismatch", failures)

    for path in (DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        require("Wave670 texel packer continuation" in text, f"Wave670 missing from {path.name}", failures)
        require("texel-packer-continuation-wave670" in text, f"Wave670 tag missing from {path.name}", failures)


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
    print("Ghidra texel packer continuation Wave670 probe")
    print(f"Status: {status}")
    print(f"Targets: {len(TARGETS)}")
    print(f"Evidence root: {BASE.relative_to(ROOT)}")
    if failures:
        for failure in failures:
            print(f"- {failure}")
    return 1 if failures and args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
