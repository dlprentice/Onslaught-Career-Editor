#!/usr/bin/env python3
"""Validate Wave671 texel callback/raw packer read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave671-texel-callback-raw-packers"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_texel_callback_raw_packers_wave671_2026-05-21.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
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
    "texel-callback-raw-packers-wave671",
    "wave671-readback-verified",
    "retail-binary-evidence",
    "signature-hardened",
    "comment-hardened",
    "texel-packer",
}

VEC4_SIGNATURE = (
    "void __thiscall {name}(void * this, uint output_x, uint output_y, "
    "float * source_vec4_array, int unused_context)"
)

RAW_SIGNATURE = (
    "void __thiscall {name}(void * this, uint output_x, uint output_y, "
    "void * source_texel_records, int unused_context)"
)

TARGETS = {
    "0x00584724": {
        "name": "CDXTexture__PackTexels_CallbackPerTexel_RepeatA",
        "signature_template": VEC4_SIGNATURE,
        "tags": {"cdxtexture", "callback-dispatch", "repeat-a", "indirect-helper", "mode-1"},
        "comment_tokens": ("repeat-A callback wrapper", "0x005759c3", "mode selector 1", "+0x1058/+0x105c/+0x20"),
        "decompile": "00584724_CDXTexture__PackTexels_CallbackPerTexel_RepeatA.c",
    },
    "0x00584786": {
        "name": "CDXTexture__PackTexels_CallbackPerTexel_RepeatB",
        "signature_template": VEC4_SIGNATURE,
        "tags": {"cdxtexture", "callback-dispatch", "repeat-b", "indirect-helper", "mode-2"},
        "comment_tokens": ("repeat-B callback wrapper", "0x005759c3", "mode selector 2", "source stride +0x10"),
        "decompile": "00584786_CDXTexture__PackTexels_CallbackPerTexel_RepeatB.c",
    },
    "0x005847e9": {
        "name": "CDXTexture__PackTexels_CallbackPerTexel_Once",
        "signature_template": VEC4_SIGNATURE,
        "tags": {"cdxtexture", "callback-dispatch", "single-call", "indirect-helper", "byte-count"},
        "comment_tokens": ("single-call callback wrapper", "byte count count*4", "0x005759c3 once"),
        "decompile": "005847e9_CDXTexture__PackTexels_CallbackPerTexel_Once.c",
    },
    "0x00584831": {
        "name": "CDXTexture__PackTexels_CopyRaw32",
        "signature_template": RAW_SIGNATURE,
        "tags": {"cdxtexture", "raw-copy", "copy-raw32", "dword-output"},
        "comment_tokens": ("raw 32-bit copy packer", "first 4 bytes", "16-byte source record"),
        "decompile": "00584831_CDXTexture__PackTexels_CopyRaw32.c",
    },
    "0x00584886": {
        "name": "CDXTexture__PackTexels_CopyRaw64",
        "signature_template": RAW_SIGNATURE,
        "tags": {"cdxtexture", "raw-copy", "copy-raw64", "qword-output"},
        "comment_tokens": ("raw 64-bit copy packer", "first 8 bytes", "16-byte source record"),
        "decompile": "00584886_CDXTexture__PackTexels_CopyRaw64.c",
    },
    "0x005848e3": {
        "name": "CDXTexture__PackTexels_CopyRaw128",
        "signature_template": RAW_SIGNATURE,
        "tags": {"cdxtexture", "raw-copy", "copy-raw128", "vec4-output"},
        "comment_tokens": ("raw 128-bit copy packer", "count*16 bytes", "MOVSD.REP"),
        "decompile": "005848e3_CDXTexture__PackTexels_CopyRaw128.c",
    },
    "0x00584936": {
        "name": "CDXTexture__PackTexels_NoDither_A16L16",
        "signature_template": VEC4_SIGNATURE,
        "tags": {"cdxtexture", "no-dither-named", "dither-term-observed", "a16l16", "dword-output", "luminance"},
        "comment_tokens": ("currently named no-dither A16L16", "+0x34 dither-table term", "weighted RGB luminance"),
        "decompile": "00584936_CDXTexture__PackTexels_NoDither_A16L16.c",
    },
    "0x00584a4c": {
        "name": "CTexture__PackTexels_NoDither_Bits16_16_16",
        "signature_template": VEC4_SIGNATURE,
        "tags": {"ctexture", "no-dither-named", "dither-term-observed", "bits16-16-16", "three-word-output"},
        "comment_tokens": ("currently named no-dither 16-16-16", "+0x34 dither-table term", "source lanes +8, +4, and +0"),
        "decompile": "00584a4c_CTexture__PackTexels_NoDither_Bits16_16_16.c",
    },
}

for data in TARGETS.values():
    data["signature"] = data["signature_template"].format(name=data["name"])

DOC_TOKENS = (
    "Wave671 texel callback/raw packers",
    "texel-callback-raw-packers-wave671",
    "0x00584724 CDXTexture__PackTexels_CallbackPerTexel_RepeatA",
    "0x00584a4c CTexture__PackTexels_NoDither_Bits16_16_16",
    "0x00584b5f CTexture__UnpackTexels_Bgr8ToFloat4",
)

OVERCLAIM_TOKENS = (
    "fully reverse-engineered",
    "runtime texture output proven",
    "exact callback ABI proven",
    "exact selector contract proven",
    "exact source-record contract proven",
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
        require("Wave671 static read-back" in comment, f"missing Wave671 comment at {address}", failures)
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
        "apply-wave671-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=8 missing=0 bad=0",
        "apply-wave671-apply.log": "SUMMARY: updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=8 missing=0 bad=0",
        "apply-wave671-final-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=8 found=8 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "post-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "post-instructions.log": "targets=8 missing=0",
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
    require("Wrote 840 instruction rows" in instructions, "instruction row count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require("test:ghidra-texel-callback-raw-packers-wave671" in package.get("scripts", {}), "package script missing", failures)
    require((ROOT / "tools" / "ApplyTexelCallbackRawPackersWave671.java").is_file(), "apply script missing", failures)

    docs = (PUBLIC_NOTE, FUNCTION_INDEX, DXTEXTURE_DOC, TEXTURE_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG)
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text, f"{token!r} missing from {path.relative_to(ROOT)}", failures)
        for token in OVERCLAIM_TOKENS:
            require(token not in text, f"overclaim token {token!r} found in {path.relative_to(ROOT)}", failures)

    for path in (LEDGER, ATTEMPT_LOG):
        text = read_text(path)
        require("Wave671 texel callback/raw packers" in text, f"Wave671 missing from {path.relative_to(ROOT)}", failures)
        require("texel-callback-raw-packers-wave671" in text, f"Wave671 tag missing from {path.relative_to(ROOT)}", failures)


def check_state(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("diffCount") == 0, "backup diffCount mismatch", failures)
    require(backup.get("fileCount") == 19, "backup fileCount mismatch", failures)
    require(int(float(backup.get("byteCount", 0))) == 163875719, "backup byteCount mismatch", failures)
    require("post_wave671_texel_callback_raw_packers_verified" in backup.get("backupPath", ""), "backup path mismatch", failures)

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6098, "queue total mismatch", failures)
    signals = queue.get("qualitySignals", {})
    require(signals.get("commentlessFunctionCount") == 2368, "queue commentless mismatch", failures)
    require(signals.get("undefinedSignatureCount") == 1217, "queue undefined-signature mismatch", failures)
    require(signals.get("paramSignatureCount") == 587, "queue param_N mismatch", failures)
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(head.get("address") == "0x00584b5f", f"queue head address mismatch: {head}", failures)
    require(head.get("name") == "CTexture__UnpackTexels_Bgr8ToFloat4", f"queue head name mismatch: {head}", failures)

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(ledger[-1].get("task") == "Wave671 texel callback/raw packers", "ledger last row mismatch", failures)
    require(attempts[-1].get("task") == "Wave671 texel callback/raw packers", "attempt task mismatch", failures)
    require(attempts[-1].get("attempt_id") == 20326, "attempt id mismatch", failures)
    require(len(ledger) == 1067, "ledger row count mismatch", failures)
    require(len(attempts) == 20327, "attempt row count mismatch", failures)

    tracking = read_json(TRACKING)
    counters = tracking.get("counters", {})
    require(tracking.get("current_focus", "").startswith("Wave671 texel callback/raw packers"), "tracking current_focus mismatch", failures)
    require(counters.get("ledger_rows") == 1067, "tracking ledger_rows mismatch", failures)
    require(counters.get("attempt_rows") == 20327, "tracking attempt_rows mismatch", failures)
    require(counters.get("completed") == 1058, "tracking completed mismatch", failures)
    require(counters.get("pending") == 9, "tracking pending mismatch", failures)
    require(tracking.get("next_attempt_id") == 20327, "tracking next_attempt_id mismatch", failures)

    for path in (DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        require("Wave671 texel callback/raw packers" in text, f"Wave671 missing from {path.name}", failures)
        require("texel-callback-raw-packers-wave671" in text, f"Wave671 tag missing from {path.name}", failures)


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
    print("Ghidra texel callback/raw packers Wave671 probe")
    print(f"Status: {status}")
    print(f"Targets: {len(TARGETS)}")
    print(f"Evidence root: {BASE.relative_to(ROOT)}")
    if failures:
        for failure in failures:
            print(f"- {failure}")
    return 1 if failures and args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
