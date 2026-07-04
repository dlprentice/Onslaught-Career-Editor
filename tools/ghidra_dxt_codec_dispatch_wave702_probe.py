#!/usr/bin/env python3
"""Validate Wave702 DXT codec / dispatch read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave702-dxt-codec-dispatch"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_dxt_codec_dispatch_wave702_2026-05-21.md"
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

BASE_TAGS = {
    "static-reaudit",
    "dxt-codec-dispatch-wave702",
    "wave702-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
}

TARGETS = {
    "0x0059764a": (
        "CDXTexture__DecodeDxt1ColorBlockToRgba",
        "int __stdcall CDXTexture__DecodeDxt1ColorBlockToRgba(float * rgba_float_block16_out, void * dxt1_color_block)",
        ("DXT1 color block", "RGB565", "two-bit selector mask"),
        BASE_TAGS | {"dxt-codec", "dxt1", "rgb565", "decode", "tranche-head"},
    ),
    "0x0059778a": (
        "CTexture__DecodeDxt3BlockToFloatRgba",
        "int __stdcall CTexture__DecodeDxt3BlockToFloatRgba(float * rgba_float_block16_out, void * dxt3_block)",
        ("block+8", "4-bit-alpha", "sixteen RGBA float4"),
        BASE_TAGS | {"dxt-codec", "dxt3", "explicit-alpha", "decode"},
    ),
    "0x0059780d": (
        "CTexture__DecodeDxt5BlockToFloatRgba",
        "int __stdcall CTexture__DecodeDxt5BlockToFloatRgba(float * rgba_float_block16_out, void * dxt5_block)",
        ("alpha ladder", "24-bit", "three-bit-selector"),
        BASE_TAGS | {"dxt-codec", "dxt5", "interpolated-alpha", "decode"},
    ),
    "0x00597949": (
        "CTexture__EncodeDxt5AlphaIndices_ErrorDiffusion",
        "int __stdcall CTexture__EncodeDxt5AlphaIndices_ErrorDiffusion(void * dxt_color_block_out, float * rgba_float_block16)",
        ("error-diffusing", "alpha lane", "alpha-mode marker"),
        BASE_TAGS | {"dxt-codec", "dxt5", "encode", "error-diffusion", "alpha-indices"},
    ),
    "0x00597a61": (
        "CFastVB__PackScalarBlock_4BitEndpoints",
        "void __stdcall CFastVB__PackScalarBlock_4BitEndpoints(void * dxt3_block_out, float * rgba_float_block16)",
        ("4-bit", "output+8", "color/alpha coupling"),
        BASE_TAGS | {"dxt-codec", "dxt3", "encode", "explicit-alpha", "selector-indices"},
    ),
    "0x00597b87": (
        "CFastVB__PackScalarBlock_InterpolatedEndpoints",
        "int __stdcall CFastVB__PackScalarBlock_InterpolatedEndpoints(void * dxt5_block_out, float * rgba_float_block16)",
        ("DXT5 alpha endpoint", "selector remap", "residual diffusion"),
        BASE_TAGS | {"dxt-codec", "dxt5", "encode", "interpolated-alpha", "selector-indices"},
    ),
    "0x00598056": (
        "CTexture__EncodeDxt3AlphaBlock",
        "void __stdcall CTexture__EncodeDxt3AlphaBlock(void * dxt3_block_out)",
        ("CTexture__PremultiplyAlphaBlock16", "DXT3", "hidden source-block ABI"),
        BASE_TAGS | {"dxt-codec", "dxt3", "encode", "premultiply-alpha"},
    ),
    "0x0059808a": (
        "CTexture__EncodeDxt5AlphaBlock",
        "int __stdcall CTexture__EncodeDxt5AlphaBlock(void * dxt5_block_out)",
        ("CTexture__PremultiplyAlphaBlock16", "DXT5", "hidden source-block ABI"),
        BASE_TAGS | {"dxt-codec", "dxt5", "encode", "premultiply-alpha"},
    ),
    "0x005980be": (
        "CFastVB__InitDispatchTableVariant_005980be",
        "void __cdecl CFastVB__InitDispatchTableVariant_005980be(void * math_dispatch_table)",
        ("math dispatch-table variant", "half-float", "slot schema"),
        BASE_TAGS | {"dispatch-table", "math-dispatch", "cpu-feature", "variant-005980be"},
    ),
    "0x0059822c": (
        "CFastVB__InitDispatchTableVariant_0059822c",
        "void __cdecl CFastVB__InitDispatchTableVariant_0059822c(void * math_dispatch_table)",
        ("alternate math dispatch-table", "SIMD half-float", "slot schema"),
        BASE_TAGS | {"dispatch-table", "math-dispatch", "cpu-feature", "variant-0059822c"},
    ),
    "0x00598474": (
        "CFastVB__InitDispatchOpsFromFeatureFlags",
        "void __cdecl CFastVB__InitDispatchOpsFromFeatureFlags(void * math_dispatch_table)",
        ("CFastVB__DetectCpuFeatureMask", "feature-mask bits", "math dispatch-table slots"),
        BASE_TAGS | {"dispatch-table", "math-dispatch", "cpu-feature", "feature-mask", "tranche-tail"},
    ),
}

DOC_TOKENS = (
    "Wave702 DXT codec / dispatch",
    "dxt-codec-dispatch-wave702",
    "0x0059764a CDXTexture__DecodeDxt1ColorBlockToRgba",
    "0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags",
    "0x00598702 CTexture__NodePayloadBaseCtor",
)

OVERCLAIM_TOKENS = (
    "runtime texture fidelity proven",
    "runtime compression quality proven",
    "dxt block abi proven",
    "dispatch-table slot schema proven",
    "cpu feature-bit names proven",
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


def check_metadata(failures: list[str]) -> None:
    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile-post" / "index.tsv")}

    expected_counts = {
        "pre-metadata.tsv": 11,
        "pre-tags.tsv": 11,
        "pre-xrefs.tsv": 17,
        "pre-instructions.tsv": 1067,
        "decompile-pre/index.tsv": 11,
        "post-metadata.tsv": 11,
        "post-tags.tsv": 11,
        "post-xrefs.tsv": 17,
        "post-instructions.tsv": 1067,
        "decompile-post/index.tsv": 11,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    for address, (name, signature, comment_tokens, expected_tags) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch at {address}", failures)
        require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
        comment = row.get("comment", "")
        require("Wave702 static read-back" in comment, f"missing Wave702 comment at {address}", failures)
        require("Static metadata only" in comment, f"missing uncertainty clause at {address}", failures)
        for token in comment_tokens:
            require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(expected_tags.issubset(actual_tags), f"tags missing at {address}: {expected_tags - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)
        require((BASE / "decompile-post" / f"{address[2:]}_{name}.c").is_file(), f"missing decompile file for {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-wave702-dry.log": "SUMMARY: updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=11 missing=0 bad=0",
        "apply-wave702-apply.log": "SUMMARY: updated=11 skipped=0 renamed=0 would_rename=0 signature_updated=11 missing=0 bad=0",
        "apply-wave702-final-dry.log": "SUMMARY: updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "pre-metadata.log": "targets=11 found=11 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=11 missing=0",
        "pre-xrefs.log": "Wrote 17 rows",
        "pre-instructions.log": "Wrote 1067 instruction rows",
        "pre-decompile.log": "targets=11 dumped=11 missing=0 failed=0",
        "post-metadata.log": "targets=11 found=11 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=11 missing=0",
        "post-xrefs.log": "Wrote 17 rows",
        "post-instructions.log": "Wrote 1067 instruction rows",
        "post-decompile.log": "targets=11 dumped=11 missing=0 failed=0",
        "queue-refresh.log": "total_functions=6098 commented_functions=4056",
        "queue-probe-after-refresh.log": "Status: PASS",
    }
    for filename, token in expected.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("REPORT: Save succeeded" in text or filename == "queue-probe-after-refresh.log", f"save report missing in {filename}", failures)
        require("Input file not found" not in text, f"bad input path found in {filename}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("ERROR REPORT SCRIPT ERROR" not in text, f"script error found in {filename}", failures)
        require("BAD:" not in text and "BADNAME:" not in text and "MISSING:" not in text, f"bad/missing marker found in {filename}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("status") == "PASS", "queue status not PASS", failures)
    require(queue.get("totalFunctions") == 6098, f"queue total mismatch: {queue.get('totalFunctions')}", failures)
    require(quality.get("commentlessFunctionCount") == 2042, f"commentless mismatch: {quality.get('commentlessFunctionCount')}", failures)
    require(quality.get("undefinedSignatureCount") == 1216, f"undefined mismatch: {quality.get('undefinedSignatureCount')}", failures)
    require(quality.get("paramSignatureCount") == 270, f"param mismatch: {quality.get('paramSignatureCount')}", failures)
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    require(head.get("address") == "0x00598702", f"next head address mismatch: {head}", failures)
    require(head.get("name") == "CTexture__NodePayloadBaseCtor", f"next head name mismatch: {head}", failures)

    rows = read_tsv(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv")
    param_re = re.compile(r"\bparam_\d+\b")
    clean = [
        row for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not param_re.search(row.get("signature", ""))
    ]
    require(len(clean) == 4002, f"strict clean proxy mismatch: {len(clean)}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backup") == "[maintainer-local-ghidra-backup-root]\\BEA_20260521-175105_post_wave702_dxt_codec_dispatch_verified", "backup path mismatch", failures)
    require(backup.get("file_count") == 19, f"backup file count mismatch: {backup.get('file_count')}", failures)
    require(int(backup.get("byte_count", -1)) == 165251975, f"backup byte count mismatch: {backup.get('byte_count')}", failures)
    require(backup.get("diff_count") == 0, f"backup diff count mismatch: {backup.get('diff_count')}", failures)


def check_docs(failures: list[str]) -> None:
    doc_paths = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        DXTEXTURE_DOC,
        FASTVB_DOC,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in doc_paths:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text, f"missing doc token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lowered, f"overclaim token found in {path.relative_to(ROOT)}: {token}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-dxt-codec-dispatch-wave702")
        == "py -3 tools\\ghidra_dxt_codec_dispatch_wave702_probe.py --check",
        "package script missing",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave702 DXT codec / dispatch" for row in ledger_rows), "ledger row missing", failures)
    require(any(row.get("task") == "Wave702 DXT codec / dispatch" and row.get("readback") == "verified" for row in attempt_rows), "attempt row missing", failures)
    tracking = read_json(TRACKING)
    require(tracking.get("next_attempt_id") == 20358, f"next_attempt_id mismatch: {tracking.get('next_attempt_id')}", failures)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    failures: list[str] = []
    check_metadata(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave702 DXT codec / dispatch probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave702 DXT codec / dispatch probe: PASS")
    print("Targets: 11")
    print("Queue: 6098 total, 4056 commented, 2042 commentless, 1216 exact-undefined, 270 param_N")
    print("Strict clean-signature proxy: 4002/6098 = 65.63%")
    print("Next head: 0x00598702 CTexture__NodePayloadBaseCtor")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
