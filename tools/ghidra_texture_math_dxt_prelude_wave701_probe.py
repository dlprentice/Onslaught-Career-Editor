#!/usr/bin/env python3
"""Validate Wave701 texture math / DXT prelude read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave701-texture-math-dxt-prelude"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_texture_math_dxt_prelude_wave701_2026-05-21.md"
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

BASE_SIGNATURE_TAGS = {
    "static-reaudit",
    "texture-math-dxt-prelude-wave701",
    "wave701-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
}

TARGETS = {
    "0x005960c1": (
        "CDXTexture__FastReciprocalSqrtScalar",
        "double __stdcall CDXTexture__FastReciprocalSqrtScalar(uint float_bits)",
        ("reciprocal square-root", "DAT_00658c98", "runtime math correctness remain unproven"),
        BASE_SIGNATURE_TAGS | {"texture-math", "reciprocal-sqrt", "lookup-table", "tranche-head"},
    ),
    "0x00596106": (
        "CDXTexture__NormalizeVec3Fast",
        "float * __stdcall CDXTexture__NormalizeVec3Fast(float * normalized_vec3_out, float * input_vec3)",
        ("zeroes normalized_vec3_out", "near-unit", "CDXTexture__FastReciprocalSqrtScalar"),
        BASE_SIGNATURE_TAGS | {"texture-math", "vec3-normalize", "reciprocal-sqrt", "dispatch-slot"},
    ),
    "0x005961d0": (
        "CDXTexture__MultiplyMatrix4x4_InPlaceSafe",
        "void __stdcall CDXTexture__MultiplyMatrix4x4_InPlaceSafe(float * matrix4x4_out, float * left_matrix4x4, float * right_matrix4x4)",
        ("4x4 float matrices", "right-matrix alias", "16-dword scratch"),
        BASE_SIGNATURE_TAGS | {"texture-math", "matrix4x4", "alias-safe", "dispatch-slot"},
    ),
    "0x005962b3": (
        "CDXTexture__MultiplyMatrix4x4_Safe",
        "void __stdcall CDXTexture__MultiplyMatrix4x4_Safe(float * matrix4x4_out, float * left_matrix4x4, float * right_matrix4x4)",
        ("4x4 float matrices", "aliases either input", "scratch result"),
        BASE_SIGNATURE_TAGS | {"texture-math", "matrix4x4", "alias-safe", "dispatch-slot"},
    ),
    "0x00596341": (
        "CFastVB__InitMathDispatchTable",
        "void __stdcall CFastVB__InitMathDispatchTable(void * math_dispatch_table)",
        ("math dispatch table", "+0x0c", "+0x88"),
        BASE_SIGNATURE_TAGS | {"texture-math", "dispatch-table", "matrix4x4", "vec3-normalize"},
    ),
    "0x00596386": (
        "CDXTexture__UnpackRgb565ToRgbaFloat",
        "void __fastcall CDXTexture__UnpackRgb565ToRgbaFloat(uint rgb565_word)",
        ("rgb565_word", "hidden EAX float4 pointer", "alpha 1.0"),
        BASE_SIGNATURE_TAGS | {"texture-codec", "rgb565", "float4", "hidden-eax-output"},
    ),
    "0x005963d2": (
        "CDXTexture__NormalizeColorBlockByAlpha",
        "int __fastcall CDXTexture__NormalizeColorBlockByAlpha(void * rgba_float_block16)",
        ("sixteen float4 RGBA", "zeroes RGB", "divides RGB by alpha"),
        BASE_SIGNATURE_TAGS | {"texture-codec", "rgba-float-block", "alpha-normalize", "dxt-prep"},
    ),
    "0x00596450": (
        "CTexture__PremultiplyAlphaBlock16",
        "int __fastcall CTexture__PremultiplyAlphaBlock16(void * premultiplied_rgba_out)",
        ("hidden-EAX source", "multiplies RGB lanes", "preserves alpha"),
        BASE_SIGNATURE_TAGS | {"texture-codec", "rgba-float-block", "premultiply-alpha", "hidden-eax-input", "dxt-prep"},
    ),
    "0x00596480": (
        "CFastVB__PackClampedRgbToR5G6B5",
        "uint __fastcall CFastVB__PackClampedRgbToR5G6B5(void * rgb_float_triplet)",
        ("clamps", "5-bit scale", "RGB565 word"),
        BASE_SIGNATURE_TAGS | {"texture-codec", "rgb565", "pack", "dxt-endpoint"},
    ),
    "0x00596589": (
        "CFastVB__SolveScalarEndpointPairFromSamples",
        "void __stdcall CFastVB__SolveScalarEndpointPairFromSamples(float * endpoint_min_out, float * endpoint_max_out, float * scalar_samples16)",
        ("sixteen scalar_samples16", "hidden EBX", "up to eight passes"),
        BASE_SIGNATURE_TAGS | {"texture-codec", "endpoint-solver", "scalar-block", "hidden-ebx-mode"},
    ),
    "0x005968a4": (
        "CFastVB__SolveVectorEndpointPairFromSamples",
        "void __stdcall CFastVB__SolveVectorEndpointPairFromSamples(float * endpoint_min_rgb_out, float * endpoint_max_rgb_out, float * rgba_samples16, int endpoint_count)",
        ("sixteen four-float sample rows", "endpoint_count 3 or 4", "RGB endpoint pair"),
        BASE_SIGNATURE_TAGS | {"texture-codec", "endpoint-solver", "rgb-vector-block", "dxt-endpoint"},
    ),
    "0x00596e23": (
        "CFastVB__QuantizeScalarBlockIndices",
        "int __stdcall CFastVB__QuantizeScalarBlockIndices(void * dxt_color_block_out, float alpha_mode_weight)",
        ("hidden-EAX", "CFastVB__SolveVectorEndpointPairFromSamples", "32-bit selector mask"),
        BASE_SIGNATURE_TAGS | {"texture-codec", "dxt-quantize", "rgb565", "selector-indices", "hidden-eax-input", "tranche-tail"},
    ),
}

DOC_TOKENS = (
    "Wave701 texture math / DXT prelude",
    "texture-math-dxt-prelude-wave701",
    "0x005960c1 CDXTexture__FastReciprocalSqrtScalar",
    "0x00596e23 CFastVB__QuantizeScalarBlockIndices",
    "0x0059764a CDXTexture__DecodeDxt1ColorBlockToRgba",
)

OVERCLAIM_TOKENS = (
    "runtime math correctness proven",
    "runtime texture fidelity proven",
    "runtime compression quality proven",
    "dxt block schema proven",
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
        "pre-metadata.tsv": 12,
        "pre-tags.tsv": 12,
        "pre-xrefs.tsv": 24,
        "pre-instructions.tsv": 1068,
        "decompile-pre/index.tsv": 12,
        "post-metadata.tsv": 12,
        "post-tags.tsv": 12,
        "post-xrefs.tsv": 24,
        "post-instructions.tsv": 1068,
        "decompile-post/index.tsv": 12,
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
        require("Wave701 static read-back" in comment, f"missing Wave701 comment at {address}", failures)
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
        "apply-wave701-dry.log": "SUMMARY: updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=12 missing=0 bad=0",
        "apply-wave701-apply.log": "SUMMARY: updated=12 skipped=0 renamed=0 would_rename=0 signature_updated=12 missing=0 bad=0",
        "apply-wave701-final-dry.log": "SUMMARY: updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "pre-metadata.log": "targets=12 found=12 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "pre-xrefs.log": "Wrote 24 rows",
        "pre-instructions.log": "Wrote 1068 instruction rows",
        "pre-decompile.log": "targets=12 dumped=12 missing=0 failed=0",
        "post-metadata.log": "targets=12 found=12 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "post-xrefs.log": "Wrote 24 rows",
        "post-instructions.log": "Wrote 1068 instruction rows",
        "post-decompile.log": "targets=12 dumped=12 missing=0 failed=0",
        "queue-refresh.log": "total_functions=6098 commented_functions=4045",
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
    require(quality.get("commentlessFunctionCount") == 2053, f"commentless mismatch: {quality.get('commentlessFunctionCount')}", failures)
    require(quality.get("undefinedSignatureCount") == 1216, f"undefined mismatch: {quality.get('undefinedSignatureCount')}", failures)
    require(quality.get("paramSignatureCount") == 281, f"param mismatch: {quality.get('paramSignatureCount')}", failures)
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    require(head.get("address") == "0x0059764a", f"next head address mismatch: {head}", failures)
    require(head.get("name") == "CDXTexture__DecodeDxt1ColorBlockToRgba", f"next head name mismatch: {head}", failures)

    rows = read_tsv(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv")
    param_re = re.compile(r"\bparam_\d+\b")
    clean = [
        row for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not param_re.search(row.get("signature", ""))
    ]
    require(len(clean) == 3991, f"strict clean proxy mismatch: {len(clean)}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(
        backup.get("backup_path").replace("\\", "/")
        == "G:/GhidraBackups/BEA_20260521-172303_post_wave701_texture_math_dxt_prelude_verified",
        "backup path mismatch",
        failures,
    )
    require(backup.get("file_count") == 19, f"backup file count mismatch: {backup}", failures)
    require(int(float(backup.get("total_bytes"))) == 165251975, f"backup bytes mismatch: {backup}", failures)
    require(backup.get("diff_count") == 0, f"backup diff mismatch: {backup}", failures)


def check_docs(failures: list[str]) -> None:
    for path in (
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
    ):
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        lower = text.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lower, f"{path.relative_to(ROOT)} contains overclaim token: {token}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-texture-math-dxt-prelude-wave701")
        == "py -3 tools\\ghidra_texture_math_dxt_prelude_wave701_probe.py --check",
        "package script missing or mismatched",
        failures,
    )

    attempt = [row for row in read_jsonl(ATTEMPT_LOG) if row.get("task") == "Wave701 texture math / DXT prelude"]
    ledger = [row for row in read_jsonl(LEDGER) if row.get("task") == "Wave701 texture math / DXT prelude"]
    require(len(attempt) == 1 and attempt[0].get("attempt_id") == 20356, "Wave701 attempt log row missing/mismatched", failures)
    require(len(ledger) == 1 and ledger[0].get("status") == "completed", "Wave701 ledger row missing/mismatched", failures)
    tracking = read_json(TRACKING)
    require(tracking.get("next_attempt_id") == 20357, "tracking next_attempt_id mismatch", failures)


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
        print("Wave701 texture math / DXT prelude probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave701 texture math / DXT prelude probe: PASS")
    print("Targets: 12")
    print("Queue: 6098 total, 4045 commented, 2053 commentless, 1216 exact-undefined, 281 param_N")
    print("Strict clean-signature proxy: 3991/6098 = 65.45%")
    print("Next head: 0x0059764a CDXTexture__DecodeDxt1ColorBlockToRgba")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
