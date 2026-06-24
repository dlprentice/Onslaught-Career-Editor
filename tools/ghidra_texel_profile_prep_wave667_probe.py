#!/usr/bin/env python3
"""Validate Wave667 texel-profile prep read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave667-texel-profile-prep"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_texel_profile_prep_wave667_2026-05-21.md"
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
    "texel-profile-prep-wave667",
    "wave667-readback-verified",
    "static-reaudit",
    "retail-binary-evidence",
    "signature-hardened",
    "comment-hardened",
}

TARGETS = {
    "0x00581263": {
        "name": "CFastVB__TexelUnpackProfile__dtor",
        "signature": "void __fastcall CFastVB__TexelUnpackProfile__dtor(void * this)",
        "tags": {"cfastvb", "texel-profile", "destructor", "scratch-release"},
        "comment_tokens": ("vtable", "+0x1054", "scratch/output pointer"),
        "decompile": "00581263_CFastVB__TexelUnpackProfile__dtor.c",
    },
    "0x00581279": {
        "name": "CFastVB__ConvertTexelVectorDomain",
        "signature": "int __thiscall CFastVB__ConvertTexelVectorDomain(void * this, float * source_vec4_array, int unused_context)",
        "tags": {"cfastvb", "texel-profile", "domain-conversion", "vec4"},
        "comment_tokens": ("source mode +0x08", "target mode +0x1050", "clamp-to-0..1"),
        "decompile": "00581279_CFastVB__ConvertTexelVectorDomain.c",
    },
    "0x0058183d": {
        "name": "CFastVB__TexelCodecProfile__dtor",
        "signature": "void __fastcall CFastVB__TexelCodecProfile__dtor(void * this)",
        "tags": {"cfastvb", "texel-codec-profile", "destructor", "nested-release"},
        "comment_tokens": ("+0x10ec", "+0x10e4", "TexelUnpackProfile__dtor"),
        "decompile": "0058183d_CFastVB__TexelCodecProfile__dtor.c",
    },
    "0x005818b7": {
        "name": "CDXTexture__PrepareDxtScaleAndQuantizedUV",
        "signature": "void __fastcall CDXTexture__PrepareDxtScaleAndQuantizedUV(void * texture_context)",
        "tags": {"cdxtexture", "dxt", "quantized-uv", "scale-prep"},
        "comment_tokens": ("DXT2/DXT3", "+0x1074", "ROUND"),
        "decompile": "005818b7_CDXTexture__PrepareDxtScaleAndQuantizedUV.c",
    },
    "0x005819b8": {
        "name": "CFastVB__LookupCurveFromRsqrtScaledInput",
        "signature": "double __stdcall CFastVB__LookupCurveFromRsqrtScaledInput(float sample_value)",
        "tags": {"cfastvb", "curve-lookup", "reciprocal-sqrt", "table-interpolate"},
        "comment_tokens": ("reciprocal-square-root", "DAT_005e96d0", "table provenance"),
        "decompile": "005819b8_CFastVB__LookupCurveFromRsqrtScaledInput.c",
    },
    "0x00581a08": {
        "name": "CFastVB__LookupCurveFromSquaredInput",
        "signature": "double __stdcall CFastVB__LookupCurveFromSquaredInput(float sample_value)",
        "tags": {"cfastvb", "curve-lookup", "squared-input", "table-interpolate"},
        "comment_tokens": ("squares sample_value", "DAT_005e9ad0", "table provenance"),
        "decompile": "00581a08_CFastVB__LookupCurveFromSquaredInput.c",
    },
    "0x00581cc0": {
        "name": "CFastVB__TexelUnpackProfile__InitConversionScratch",
        "signature": "int __thiscall CFastVB__TexelUnpackProfile__InitConversionScratch(void * this, void * peer_profile, int unused_context)",
        "tags": {"cfastvb", "texel-profile", "scratch-init", "vec4"},
        "comment_tokens": ("peer_profile +0x08", "count<<4", "+0x1054"),
        "decompile": "00581cc0_CFastVB__TexelUnpackProfile__InitConversionScratch.c",
    },
    "0x00581d49": {
        "name": "CDXTexture__ProbeTexelProfileSample",
        "signature": "void __fastcall CDXTexture__ProbeTexelProfileSample(void * texel_profile)",
        "tags": {"cdxtexture", "texel-profile", "sample-probe", "vtable-callback"},
        "comment_tokens": ("sample one vec4", "vtable slots +8 and +4", "restores the saved fields"),
        "decompile": "00581d49_CDXTexture__ProbeTexelProfileSample.c",
    },
    "0x00581e1c": {
        "name": "CFastVB__TexelUnpackProfile__ZeroTexelsMatchingKeyColor",
        "signature": "void __thiscall CFastVB__TexelUnpackProfile__ZeroTexelsMatchingKeyColor(void * this, float * texel_vec4_array, uint unused_context)",
        "tags": {"cfastvb", "texel-profile", "color-key", "zero-texel"},
        "comment_tokens": ("exactly match the key vec4", "+0x24/+0x28/+0x2c/+0x30", "runtime transparency behavior"),
        "decompile": "00581e1c_CFastVB__TexelUnpackProfile__ZeroTexelsMatchingKeyColor.c",
    },
    "0x00581e8c": {
        "name": "CDXTexture__NormalizeAndCopyVec4Array",
        "signature": "int __thiscall CDXTexture__NormalizeAndCopyVec4Array(void * this, float * source_vec4_array, int unused_context)",
        "tags": {"cdxtexture", "texel-profile", "vec4-normalize", "scratch-copy"},
        "comment_tokens": ("+0x1054", "modes 1/4 normalize RGB", "runtime image quality"),
        "decompile": "00581e8c_CDXTexture__NormalizeAndCopyVec4Array.c",
    },
}

DOC_TOKENS = (
    "Wave667 texel-profile prep",
    "texel-profile-prep-wave667",
    "0x00581263 CFastVB__TexelUnpackProfile__dtor",
    "0x00581e8c CDXTexture__NormalizeAndCopyVec4Array",
    "0x0058210e CTexture__PostProcessDecodedTexels_GammaOrSquare",
)

OVERCLAIM_TOKENS = (
    "fully reverse-engineered",
    "fully recovered",
    "runtime texture conversion behavior proven",
    "runtime transparency behavior proven",
    "exact texel-profile ABI proven",
    "exact texel-domain enum proven",
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
        require("Wave667 static read-back" in comment, f"missing Wave667 comment at {address}", failures)
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
        "apply-wave667-dry.log": "SUMMARY: updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=10 missing=0 bad=0",
        "apply-wave667-apply.log": "SUMMARY: updated=10 skipped=0 renamed=0 would_rename=0 signature_updated=10 missing=0 bad=0",
        "apply-wave667-final-dry.log": "SUMMARY: updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=10 found=10 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "post-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "post-instructions.log": "targets=10 missing=0",
        "post-xrefs.log": "Wrote 180 rows",
    }
    for filename, token in expected_exact.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"save report missing in {filename}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("ERROR REPORT SCRIPT ERROR" not in text, f"script error found in {filename}", failures)
        require("BAD:" not in text and "BADNAME:" not in text and "MISSING:" not in text, f"bad/missing marker found in {filename}", failures)

    instructions = read_text(BASE / "post-instructions.log")
    require("Wrote 870 instruction rows" in instructions, "instruction row count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require("test:ghidra-texel-profile-prep-wave667" in package.get("scripts", {}), "package script missing", failures)

    for path in (PUBLIC_NOTE, FUNCTION_INDEX, DXTEXTURE_DOC, FASTVB_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG):
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text, f"{token!r} missing from {path.relative_to(ROOT)}", failures)
        for token in OVERCLAIM_TOKENS:
            require(token not in text, f"overclaim token {token!r} found in {path.relative_to(ROOT)}", failures)

    for path in (LEDGER, ATTEMPT_LOG):
        text = read_text(path)
        require("Wave667 texel-profile prep" in text, f"Wave667 missing from {path.relative_to(ROOT)}", failures)
        require("texel-profile-prep-wave667" in text, f"Wave667 tag missing from {path.relative_to(ROOT)}", failures)


def check_state(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("diffCount") == 0, "backup diffCount mismatch", failures)
    require(backup.get("fileCount") == 19, "backup fileCount mismatch", failures)
    require(int(float(backup.get("byteCount", 0))) == 163646343, "backup byteCount mismatch", failures)
    require("post_wave667_texel_profile_verified" in backup.get("backupPath", ""), "backup path mismatch", failures)

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6098, "queue total mismatch", failures)
    signals = queue.get("qualitySignals", {})
    require(signals.get("commentlessFunctionCount") == 2409, "queue commentless mismatch", failures)
    require(signals.get("undefinedSignatureCount") == 1217, "queue undefined-signature mismatch", failures)
    require(signals.get("paramSignatureCount") == 628, "queue param_N mismatch", failures)
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(head.get("address") == "0x0058210e", f"queue head address mismatch: {head}", failures)
    require(head.get("name") == "CTexture__PostProcessDecodedTexels_GammaOrSquare", f"queue head name mismatch: {head}", failures)

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(ledger[-1].get("task") == "Wave667 texel-profile prep", "ledger last row mismatch", failures)
    require(attempts[-1].get("task") == "Wave667 texel-profile prep", "attempt task mismatch", failures)
    require(attempts[-1].get("attempt_id") == 20322, "attempt id mismatch", failures)
    require(len(ledger) == 1063, "ledger row count mismatch", failures)
    require(len(attempts) == 20323, "attempt row count mismatch", failures)

    tracking = read_json(TRACKING)
    counters = tracking.get("counters", {})
    require(tracking.get("current_focus", "").startswith("Wave667 texel-profile prep"), "tracking current_focus mismatch", failures)
    require(counters.get("ledger_rows") == 1063, "tracking ledger_rows mismatch", failures)
    require(counters.get("attempt_rows") == 20323, "tracking attempt_rows mismatch", failures)
    require(counters.get("completed") == 1054, "tracking completed mismatch", failures)
    require(counters.get("pending") == 9, "tracking pending mismatch", failures)
    require(tracking.get("next_attempt_id") == 20323, "tracking next_attempt_id mismatch", failures)

    for path in (DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        require("Wave667 texel-profile prep" in text, f"Wave667 missing from {path.name}", failures)
        require("texel-profile-prep-wave667" in text, f"Wave667 tag missing from {path.name}", failures)


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
    print("Ghidra texel-profile prep Wave667 probe")
    print(f"Status: {status}")
    print(f"Targets: {len(TARGETS)}")
    print(f"Evidence root: {BASE.relative_to(ROOT)}")
    if failures:
        for failure in failures:
            print(f"- {failure}")
    return 1 if failures and args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
