#!/usr/bin/env python3
"""Validate Wave675 texel codec continuation read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave675-texel-codec-continuation"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_texel_codec_continuation_wave675_2026-05-21.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
TEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Texture.cpp" / "_index.md"
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

CTOR_SIGNATURE = "void * __thiscall {name}(void * this, void * format_descriptor)"
UNPACK_SIGNATURE = (
    "void __thiscall {name}(void * this, uint source_x, uint source_y, "
    "float * destination_vec4_array, int unused_context)"
)
FLUSH_SIGNATURE = "int __fastcall {name}(void * profile)"
DECODE_SIGNATURE = "int __thiscall {name}(void * this, int row_index, uint column_index, uint decode_if_needed)"
BLOCK_READ_SIGNATURE = (
    "void __thiscall {name}(void * this, uint block_x, uint block_y, "
    "float * destination_vec4_array, int unused_context)"
)
BLOCK_WRITE_SIGNATURE = (
    "void __thiscall {name}(void * this, uint block_x, uint block_y, "
    "float * source_vec4_array, int unused_context)"
)
DTOR_SIGNATURE = "void __fastcall {name}(void * this)"

BASE_TAGS = {
    "static-reaudit",
    "texel-codec-continuation-wave675",
    "wave675-readback-verified",
    "retail-binary-evidence",
    "signature-hardened",
    "comment-hardened",
}
UNPACK_TAGS = BASE_TAGS | {
    "texel-unpacker",
    "ctexture",
    "bits16-16-16",
    "float4-output",
    "keycolor-zero-gate",
    "postprocess-gate",
}
PROFILE_TAGS = BASE_TAGS | {"texel-unpack-profile", "format-factory-case", "vtable-binding"}
REGISTRY_TAGS = BASE_TAGS | {"texel-unpack-profile-registry", "format-factory-case", "scratch-row-window"}
CODEC_PROFILE_TAGS = BASE_TAGS | {"texel-codec-profile", "format-factory-case", "dxt-codec", "vtable-binding"}

TARGETS = {
    "0x005869b0": ("CTexture__UnpackTexels_Bits16_16_16_ToFloat4", UNPACK_SIGNATURE, UNPACK_TAGS),
    "0x00586a55": ("CFastVB__TexelUnpackProfile_005ea128__ctor", CTOR_SIGNATURE, PROFILE_TAGS | {"vtable-005ea128"}),
    "0x00586a71": ("CFastVB__TexelUnpackProfileRegistry_005ea138__ctor", CTOR_SIGNATURE, REGISTRY_TAGS | {"fourcc-component-shifts", "vtable-005ea138"}),
    "0x00586b63": ("CFastVB__TexelUnpackProfile_005ea148__ctor", CTOR_SIGNATURE, PROFILE_TAGS | {"vtable-005ea148"}),
    "0x00586b7f": ("CFastVB__TexelUnpackProfile_005ea158__ctor", CTOR_SIGNATURE, PROFILE_TAGS | {"vtable-005ea158"}),
    "0x00586b9b": ("CFastVB__TexelUnpackProfile_005ea168__ctor", CTOR_SIGNATURE, PROFILE_TAGS | {"vtable-005ea168"}),
    "0x00586bb7": ("CFastVB__FlushPendingConvertedRows16", FLUSH_SIGNATURE, BASE_TAGS | {"texel-codec-flush", "scratch-row-window", "yuv-rgb-conversion", "component-shift-pack", "dirty-flag-clear"}),
    "0x00586ec7": ("CFastVB__InitTexelUnpackVTable_005ea198", CTOR_SIGNATURE, PROFILE_TAGS | {"vtable-005ea198"}),
    "0x00586ee3": ("CFastVB__TexelUnpackProfile_005ea1a8__ctor", CTOR_SIGNATURE, PROFILE_TAGS | {"vtable-005ea1a8"}),
    "0x00586eff": ("CFastVB__TexelUnpackProfile_005ea1b8__ctor", CTOR_SIGNATURE, PROFILE_TAGS | {"vtable-005ea1b8"}),
    "0x00586f1b": ("CFastVB__TexelUnpackProfile_005ea1c8__ctor", CTOR_SIGNATURE, PROFILE_TAGS | {"vtable-005ea1c8"}),
    "0x00586f37": ("CFastVB__DecodeRowWindowToScratchPairs", DECODE_SIGNATURE, BASE_TAGS | {"texel-codec-decode", "scratch-row-window", "two-pixel-pairs", "yuv-rgb-conversion", "component-shift-unpack"}),
    "0x00587303": ("CFastVB__TexelUnpackProfile_005ea1f4__ctor", CTOR_SIGNATURE, PROFILE_TAGS | {"vtable-005ea1f4"}),
    "0x00587322": ("CFastVB__TexelUnpackProfile_005ea204__ctor", CTOR_SIGNATURE, PROFILE_TAGS | {"vtable-005ea204"}),
    "0x0058733e": ("CFastVB__TexelUnpackProfile_005ea214__ctor", CTOR_SIGNATURE, PROFILE_TAGS | {"vtable-005ea214"}),
    "0x0058735a": ("CFastVB__StoreDecodedBlockToScratch", BLOCK_WRITE_SIGNATURE, BASE_TAGS | {"texel-codec-store", "scratch-row-window", "vec4-block-copy", "dirty-flag-set", "domain-conversion"}),
    "0x005873f8": ("CFastVB__LoadDecodedBlockFromScratch", BLOCK_READ_SIGNATURE, BASE_TAGS | {"texel-codec-load", "scratch-row-window", "vec4-block-copy", "keycolor-zero-gate", "postprocess-gate"}),
    "0x00587477": ("CFastVB__TexelCodecProfile__ctorFromFourCC", CTOR_SIGNATURE, BASE_TAGS | {"texel-codec-profile", "fourcc-dispatch", "dxt-codec", "quad-cache", "aligned-block-window"}),
    "0x00587663": ("CFastVB__TexelCodecProfile_005ea224__ctor", CTOR_SIGNATURE, CODEC_PROFILE_TAGS | {"vtable-005ea224"}),
    "0x0058767b": ("CFastVB__TexelCodecProfile_005ea234__ctor", CTOR_SIGNATURE, CODEC_PROFILE_TAGS | {"vtable-005ea234"}),
    "0x00587693": ("CFastVB__TexelCodecProfile_005ea244__ctor", CTOR_SIGNATURE, CODEC_PROFILE_TAGS | {"vtable-005ea244"}),
    "0x005876ab": ("CTexture__WriteTexelBlockWithQuadCache", BLOCK_WRITE_SIGNATURE, BASE_TAGS | {"texel-codec-write", "ctexture", "quad-cache", "dxt-codec", "encode-callback", "vec4-block-copy"}),
    "0x00587af0": ("CTexture__ReadTexelBlockWithQuadCache", BLOCK_READ_SIGNATURE, BASE_TAGS | {"texel-codec-read", "ctexture", "quad-cache", "dxt-codec", "decode-callback", "keycolor-zero-gate", "postprocess-gate"}),
    "0x00587daf": ("CFastVB__TexelPackProfile_scalar_deleting_dtor", DTOR_SIGNATURE, BASE_TAGS | {"texel-codec-dtor", "scratch-buffer-free", "flush-before-dtor", "destructor-like"}),
    "0x00587dd6": ("CFastVB__TexelUnpackProfileRegistry_005ea254__ctor", CTOR_SIGNATURE, REGISTRY_TAGS | {"vtable-binding", "vtable-005ea254"}),
}

DOC_TOKENS = (
    "Wave675 texel codec continuation",
    "texel-codec-continuation-wave675",
    "0x005869b0 CTexture__UnpackTexels_Bits16_16_16_ToFloat4",
    "0x00587dd6 CFastVB__TexelUnpackProfileRegistry_005ea254__ctor",
    "0x00587dee CFastVB__InitTexelUnpackVTable_005ea264",
)

OVERCLAIM_TOKENS = (
    "fully reverse-engineered",
    "runtime texture output proven",
    "exact profile ABI proven",
    "FourCC semantics proven",
    "DXT block ABI proven",
    "quad-cache contract proven",
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

    for address, (name, signature_template, expected_tags) in TARGETS.items():
        expected_signature = signature_template.format(name=name)
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch at {address}: {row.get('name')}", failures)
        require(row.get("signature") == expected_signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}: {row.get('status')}", failures)
        comment = row.get("comment", "")
        require("Wave675 static read-back" in comment, f"missing Wave675 comment at {address}", failures)
        require("Static metadata only" in comment, f"missing uncertainty clause at {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(expected_tags.issubset(actual_tags), f"tags missing at {address}: {expected_tags - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}: {tag_row.get('status')}", failures)

        decompile_row = decompile_index.get(address)
        require(decompile_row is not None, f"missing decompile index for {address}", failures)
        if decompile_row is not None:
            require(decompile_row.get("signature") == expected_signature, f"decompile signature mismatch at {address}", failures)
            require(decompile_row.get("status") == "OK", f"decompile status mismatch at {address}", failures)
        require((BASE / "decompile-post" / f"{address[2:]}_{name}.c").is_file(), f"missing decompile file for {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected_exact = {
        "apply-wave675-dry.log": "SUMMARY: updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 missing=0 bad=0",
        "apply-wave675-apply.log": "SUMMARY: updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 missing=0 bad=0",
        "apply-wave675-final-dry.log": "SUMMARY: updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=25 found=25 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=25 missing=0",
        "post-decompile.log": "targets=25 dumped=25 missing=0 failed=0",
        "post-instructions.log": "targets=25 missing=0",
        "post-xrefs.log": "Wrote 52 rows",
    }
    for filename, token in expected_exact.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"save report missing in {filename}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("ERROR REPORT SCRIPT ERROR" not in text, f"script error found in {filename}", failures)
        require("BAD:" not in text and "BADNAME:" not in text and "MISSING:" not in text, f"bad/missing marker found in {filename}", failures)

    instructions = read_text(BASE / "post-instructions.log")
    require("Wrote 1125 instruction rows" in instructions, "instruction row count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require("test:ghidra-texel-codec-continuation-wave675" in package.get("scripts", {}), "package script missing", failures)
    require((ROOT / "tools" / "ApplyTexelCodecContinuationWave675.java").is_file(), "apply script missing", failures)

    docs = (PUBLIC_NOTE, FUNCTION_INDEX, TEXTURE_DOC, FASTVB_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG)
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text, f"{token!r} missing from {path.relative_to(ROOT)}", failures)
        for token in OVERCLAIM_TOKENS:
            require(token not in text, f"overclaim token {token!r} found in {path.relative_to(ROOT)}", failures)

    for path in (LEDGER, ATTEMPT_LOG):
        text = read_text(path)
        require("Wave675 texel codec continuation" in text, f"Wave675 missing from {path.relative_to(ROOT)}", failures)
        require("texel-codec-continuation-wave675" in text, f"Wave675 tag missing from {path.relative_to(ROOT)}", failures)


def check_state(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("diffCount") == 0, "backup diffCount mismatch", failures)
    require(backup.get("fileCount") == 19, "backup fileCount mismatch", failures)
    require(int(float(backup.get("byteCount", 0))) == 164301703, "backup byteCount mismatch", failures)
    require("post_wave675_texel_codec_continuation_verified" in backup.get("backupPath", ""), "backup path mismatch", failures)

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6098, "queue total mismatch", failures)
    signals = queue.get("qualitySignals", {})
    require(signals.get("commentlessFunctionCount") == 2277, "queue commentless mismatch", failures)
    require(signals.get("undefinedSignatureCount") == 1217, "queue undefined-signature mismatch", failures)
    require(signals.get("paramSignatureCount") == 496, "queue param_N mismatch", failures)
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(head.get("address") == "0x00587dee", f"queue head address mismatch: {head}", failures)
    require(head.get("name") == "CFastVB__InitTexelUnpackVTable_005ea264", f"queue head name mismatch: {head}", failures)

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(ledger[-1].get("task") == "Wave675 texel codec continuation", "ledger last row mismatch", failures)
    require(attempts[-1].get("task") == "Wave675 texel codec continuation", "attempt task mismatch", failures)
    require(attempts[-1].get("attempt_id") == 20330, "attempt id mismatch", failures)
    require(len(ledger) == 1071, "ledger row count mismatch", failures)
    require(len(attempts) == 20331, "attempt row count mismatch", failures)

    tracking = read_json(TRACKING)
    counters = tracking.get("counters", {})
    require(tracking.get("current_focus", "").startswith("Wave675 texel codec continuation"), "tracking current_focus mismatch", failures)
    require(counters.get("ledger_rows") == 1071, "tracking ledger_rows mismatch", failures)
    require(counters.get("attempt_rows") == 20331, "tracking attempt_rows mismatch", failures)
    require(counters.get("completed") == 1062, "tracking completed mismatch", failures)
    require(counters.get("pending") == 9, "tracking pending mismatch", failures)
    require(tracking.get("next_attempt_id") == 20331, "tracking next_attempt_id mismatch", failures)

    for path in (DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        require("Wave675 texel codec continuation" in text, f"Wave675 missing from {path.name}", failures)
        require("texel-codec-continuation-wave675" in text, f"Wave675 tag missing from {path.name}", failures)


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
    print("Ghidra texel codec continuation Wave675 probe")
    print(f"Status: {status}")
    print(f"Targets: {len(TARGETS)}")
    print(f"Evidence root: {BASE.relative_to(ROOT)}")
    if failures:
        for failure in failures:
            print(f"- {failure}")
    return 1 if failures and args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
