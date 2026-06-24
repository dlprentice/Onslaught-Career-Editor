#!/usr/bin/env python3
"""Validate Wave672 texel unpack head read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave672-texel-unpack-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_texel_unpack_head_wave672_2026-05-21.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
TEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "texture.cpp" / "_index.md"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
MESH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MeshCollisionVolume.cpp" / "_index.md"
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
    "texel-unpack-head-wave672",
    "wave672-readback-verified",
    "retail-binary-evidence",
    "signature-hardened",
    "comment-hardened",
    "texel-unpacker",
    "float4-output",
    "source-pointer-fields",
    "keycolor-zero-gate",
    "postprocess-gate",
}

SIGNATURE = (
    "void __thiscall {name}(void * this, uint source_x, uint source_y, "
    "float * destination_vec4_array, int unused_context)"
)

TARGETS = {
    "0x00584b5f": {
        "name": "CTexture__UnpackTexels_Bgr8ToFloat4",
        "tags": {"ctexture", "bgr8", "alpha-one", "byte-span-106c", "three-byte-source-stride"},
        "comment_tokens": ("BGR8 unpacker", "+0x106c", "bytes 2/1/0", "key-color zeroing"),
    },
    "0x00584c04": {
        "name": "CTexture__UnpackTexels_Bgra8ToFloat4",
        "tags": {"ctexture", "bgra8", "eight-bit-scale", "four-byte-source-stride"},
        "comment_tokens": ("BGRA8 unpacker", "bytes 2/1/0/3", "observed 8-bit factor"),
    },
    "0x00584cc3": {
        "name": "CTexture__UnpackTexels_Bgr8ToFloat4_AlphaOne",
        "tags": {"ctexture", "bgr8", "alpha-one", "four-byte-source-stride", "current-name-retained"},
        "comment_tokens": ("current-name BGR8 alpha-one", "4-byte source records", "current-name/stride rationale"),
    },
    "0x00584d78": {
        "name": "CFastVB__UnpackTexels_Bits565ToFloat4",
        "tags": {"cfastvb", "rgb565", "bits565", "alpha-one", "sixteen-bit-source"},
        "comment_tokens": ("RGB565 unpacker", "5/6/5-bit lanes", "alpha 1.0"),
    },
    "0x00584e32": {
        "name": "CFastVB__UnpackTexels_Bits555ToFloat4_AlphaOne",
        "tags": {"cfastvb", "bits555", "alpha-one", "sixteen-bit-source"},
        "comment_tokens": ("5-5-5 alpha-one", "three 5-bit color lanes", "alpha 1.0"),
    },
    "0x00584ee9": {
        "name": "CFastVB__UnpackTexels_Bits1555ToFloat4",
        "tags": {"cfastvb", "bits1555", "alpha-bit", "sixteen-bit-source"},
        "comment_tokens": ("1-5-5-5 unpacker", "high-bit alpha lane"),
    },
    "0x00584fae": {
        "name": "CFastVB__UnpackTexels_Bits4444ToFloat4",
        "tags": {"cfastvb", "bits4444", "nibble-lanes", "sixteen-bit-source"},
        "comment_tokens": ("4-4-4-4 unpacker", "four 4-bit lanes"),
    },
    "0x00585072": {
        "name": "CFastVB__UnpackTexels_Bits2_10_10_10_ToFloat4",
        "tags": {"cfastvb", "bits2-10-10-10", "ten-bit-lanes", "two-bit-alpha", "dword-source"},
        "comment_tokens": ("2-10-10-10 unpacker", "low/mid/high 10-bit fields", "top 2 bits"),
    },
    "0x00585161": {
        "name": "CFastVB__UnpackTexels_Bits8888ToFloat4",
        "tags": {"cfastvb", "bits8888", "eight-bit-scale", "dword-source"},
        "comment_tokens": ("8-8-8-8 unpacker", "four byte lanes"),
    },
    "0x00585220": {
        "name": "CFastVB__UnpackTexels_Bits888ToFloat4_AlphaOne",
        "tags": {"cfastvb", "bits888", "alpha-one", "eight-bit-scale", "dword-source"},
        "comment_tokens": ("8-8-8 alpha-one", "three byte lanes", "alpha 1.0"),
    },
    "0x005852d5": {
        "name": "CFastVB__UnpackTexels_Bits16_16_ToFloat4_RG",
        "tags": {"cfastvb", "bits16-16-rg", "alpha-one", "blue-one", "dword-source"},
        "comment_tokens": ("16-16 RG unpacker", "B=1.0 and A=1.0"),
    },
    "0x00585380": {
        "name": "CFastVB__UnpackTexels_Bits2_10_10_10_ToFloat4_Alt",
        "tags": {"cfastvb", "bits2-10-10-10", "alternate-lane-order", "ten-bit-lanes", "two-bit-alpha", "dword-source"},
        "comment_tokens": ("alternate 2-10-10-10", "high/mid/low 10-bit fields", "alternate lane-order"),
    },
    "0x0058546f": {
        "name": "CMeshCollisionVolume__UnpackTexels_Bits16_16_16_16_ToFloat4",
        "tags": {"cmeshcollisionvolume", "current-owner-retained", "bits16-16-16-16", "qword-source", "aullshr-observed"},
        "comment_tokens": ("current-owner 16-16-16-16", "two dwords per texel", "__aullshr", "current owner/layout identity"),
    },
    "0x00585576": {
        "name": "CDXTexture__UnpackTexels_Bits332ToFloat4",
        "tags": {"cdxtexture", "bits332", "alpha-one", "byte-source"},
        "comment_tokens": ("3-3-2 unpacker", "3/3/2-bit RGB lanes", "alpha 1.0"),
    },
    "0x0058562d": {
        "name": "CDXTexture__UnpackTexels_A8ToFloat4_ZeroRGB",
        "tags": {"cdxtexture", "a8-zero-rgb", "alpha-byte", "byte-source", "zero-rgb"},
        "comment_tokens": ("A8 unpacker", "zero RGB", "byte-scaled alpha"),
    },
    "0x005856b8": {
        "name": "CDXTexture__UnpackTexels_Bits332A8ToFloat4",
        "tags": {"cdxtexture", "bits332-a8", "alpha-byte", "two-byte-source"},
        "comment_tokens": ("3-3-2 plus A8", "first byte as 3/3/2 RGB", "second byte as alpha"),
    },
}

for data in TARGETS.values():
    data["signature"] = SIGNATURE.format(name=data["name"])
    data["decompile"] = f"{next(addr for addr, row in TARGETS.items() if row is data)[2:]}_{data['name']}.c"

DOC_TOKENS = (
    "Wave672 texel unpack head",
    "texel-unpack-head-wave672",
    "0x00584b5f CTexture__UnpackTexels_Bgr8ToFloat4",
    "0x005856b8 CDXTexture__UnpackTexels_Bits332A8ToFloat4",
    "0x0058577f CFastVB__TexelUnpackProfile_005e9f3c__ctor",
)

OVERCLAIM_TOKENS = (
    "fully reverse-engineered",
    "runtime texture output proven",
    "exact profile ABI proven",
    "format-table contract proven",
    "lane-order enum contract proven",
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
        require("Wave672 static read-back" in comment, f"missing Wave672 comment at {address}", failures)
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
        "apply-wave672-dry.log": "SUMMARY: updated=0 skipped=16 renamed=0 would_rename=0 signature_updated=16 missing=0 bad=0",
        "apply-wave672-apply.log": "SUMMARY: updated=16 skipped=0 renamed=0 would_rename=0 signature_updated=16 missing=0 bad=0",
        "apply-wave672-final-dry.log": "SUMMARY: updated=0 skipped=16 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=16 found=16 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=16 missing=0",
        "post-decompile.log": "targets=16 dumped=16 missing=0 failed=0",
        "post-instructions.log": "targets=16 missing=0",
        "post-xrefs.log": "Wrote 16 rows",
    }
    for filename, token in expected_exact.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"save report missing in {filename}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("ERROR REPORT SCRIPT ERROR" not in text, f"script error found in {filename}", failures)
        require("BAD:" not in text and "BADNAME:" not in text and "MISSING:" not in text, f"bad/missing marker found in {filename}", failures)

    instructions = read_text(BASE / "post-instructions.log")
    require("Wrote 1616 instruction rows" in instructions, "instruction row count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require("test:ghidra-texel-unpack-head-wave672" in package.get("scripts", {}), "package script missing", failures)
    require((ROOT / "tools" / "ApplyTexelUnpackHeadWave672.java").is_file(), "apply script missing", failures)

    docs = (PUBLIC_NOTE, FUNCTION_INDEX, TEXTURE_DOC, FASTVB_DOC, DXTEXTURE_DOC, MESH_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG)
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text, f"{token!r} missing from {path.relative_to(ROOT)}", failures)
        for token in OVERCLAIM_TOKENS:
            require(token not in text, f"overclaim token {token!r} found in {path.relative_to(ROOT)}", failures)

    for path in (LEDGER, ATTEMPT_LOG):
        text = read_text(path)
        require("Wave672 texel unpack head" in text, f"Wave672 missing from {path.relative_to(ROOT)}", failures)
        require("texel-unpack-head-wave672" in text, f"Wave672 tag missing from {path.relative_to(ROOT)}", failures)


def check_state(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("diffCount") == 0, "backup diffCount mismatch", failures)
    require(backup.get("fileCount") == 19, "backup fileCount mismatch", failures)
    require(int(float(backup.get("byteCount", 0))) == 163941255, "backup byteCount mismatch", failures)
    require("post_wave672_texel_unpack_head_verified" in backup.get("backupPath", ""), "backup path mismatch", failures)

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6098, "queue total mismatch", failures)
    signals = queue.get("qualitySignals", {})
    require(signals.get("commentlessFunctionCount") == 2352, "queue commentless mismatch", failures)
    require(signals.get("undefinedSignatureCount") == 1217, "queue undefined-signature mismatch", failures)
    require(signals.get("paramSignatureCount") == 571, "queue param_N mismatch", failures)
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(head.get("address") == "0x0058577f", f"queue head address mismatch: {head}", failures)
    require(head.get("name") == "CFastVB__TexelUnpackProfile_005e9f3c__ctor", f"queue head name mismatch: {head}", failures)

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(ledger[-1].get("task") == "Wave672 texel unpack head", "ledger last row mismatch", failures)
    require(attempts[-1].get("task") == "Wave672 texel unpack head", "attempt task mismatch", failures)
    require(attempts[-1].get("attempt_id") == 20327, "attempt id mismatch", failures)
    require(len(ledger) == 1068, "ledger row count mismatch", failures)
    require(len(attempts) == 20328, "attempt row count mismatch", failures)

    tracking = read_json(TRACKING)
    counters = tracking.get("counters", {})
    require(tracking.get("current_focus", "").startswith("Wave672 texel unpack head"), "tracking current_focus mismatch", failures)
    require(counters.get("ledger_rows") == 1068, "tracking ledger_rows mismatch", failures)
    require(counters.get("attempt_rows") == 20328, "tracking attempt_rows mismatch", failures)
    require(counters.get("completed") == 1059, "tracking completed mismatch", failures)
    require(counters.get("pending") == 9, "tracking pending mismatch", failures)
    require(tracking.get("next_attempt_id") == 20328, "tracking next_attempt_id mismatch", failures)

    for path in (DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        require("Wave672 texel unpack head" in text, f"Wave672 missing from {path.name}", failures)
        require("texel-unpack-head-wave672" in text, f"Wave672 tag missing from {path.name}", failures)


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
    print("Ghidra texel unpack head Wave672 probe")
    print(f"Status: {status}")
    print(f"Targets: {len(TARGETS)}")
    print(f"Evidence root: {BASE.relative_to(ROOT)}")
    if failures:
        for failure in failures:
            print(f"- {failure}")
    return 1 if failures and args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
