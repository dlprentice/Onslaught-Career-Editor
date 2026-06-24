#!/usr/bin/env python3
"""Validate Wave673 texel unpack continuation read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave673-texel-unpack-continuation"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_texel_unpack_continuation_wave673_2026-05-21.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
TEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Texture.cpp" / "_index.md"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
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

PROFILE_SIGNATURE = "void * __thiscall {name}(void * this, void * format_descriptor)"
UNPACK_SIGNATURE = (
    "void __thiscall {name}(void * this, uint source_x, uint source_y, "
    "float * destination_vec4_array, int unused_context)"
)
DTOR_SIGNATURE = "void * __thiscall {name}(void * this, byte flags)"

BASE_TAGS = {
    "static-reaudit",
    "texel-unpack-continuation-wave673",
    "wave673-readback-verified",
    "retail-binary-evidence",
    "signature-hardened",
    "comment-hardened",
}
PROFILE_TAGS = BASE_TAGS | {"texel-unpack-profile", "format-factory-case", "vtable-binding"}
UNPACK_TAGS = BASE_TAGS | {
    "texel-unpacker",
    "float4-output",
    "source-pointer-fields",
    "keycolor-zero-gate",
    "postprocess-gate",
}
DTOR_TAGS = BASE_TAGS | {"texel-unpack-profile", "scalar-deleting-dtor", "optional-free"}

TARGETS = {
    "0x0058577f": ("CFastVB__TexelUnpackProfile_005e9f3c__ctor", PROFILE_SIGNATURE, PROFILE_TAGS | {"case-0x14", "vtable-005e9f3c"}),
    "0x0058579b": ("CTexture__UnpackTexels_Bits444ToFloat4_AlphaOne", UNPACK_SIGNATURE, UNPACK_TAGS | {"ctexture", "bits444", "alpha-one", "nibble-lanes", "two-byte-source"}),
    "0x0058584f": ("CFastVB__TexelUnpackProfile_005e9f4c__ctor", PROFILE_SIGNATURE, PROFILE_TAGS | {"case-0x15", "vtable-005e9f4c"}),
    "0x0058586b": ("CTexture__UnpackTexels_PaletteIndexA8ToFloat4", UNPACK_SIGNATURE, UNPACK_TAGS | {"ctexture", "palette-index", "alpha-byte", "two-byte-source", "palette-this-38"}),
    "0x00585908": ("CFastVB__InitTexelUnpackVTable_005e9f5c", PROFILE_SIGNATURE, PROFILE_TAGS | {"case-0x16", "vtable-005e9f5c", "current-name-retained"}),
    "0x00585924": ("CFastVB__InitTexelUnpackVTable_005e9f6c", PROFILE_SIGNATURE, PROFILE_TAGS | {"case-0x17", "vtable-005e9f6c", "current-name-retained"}),
    "0x005859bc": ("CFastVB__InitTexelUnpackVTable_005e9f7c", PROFILE_SIGNATURE, PROFILE_TAGS | {"case-0x18", "vtable-005e9f7c", "current-name-retained"}),
    "0x005859d8": ("CFastVB__UnpackTexels_L8ToFloat4", UNPACK_SIGNATURE, UNPACK_TAGS | {"cfastvb", "l8", "luminance", "alpha-one", "byte-source"}),
    "0x00585a5f": ("CFastVB__TexelUnpackProfile_005e9f8c__ctor", PROFILE_SIGNATURE, PROFILE_TAGS | {"case-0x19", "vtable-005e9f8c"}),
    "0x00585a7b": ("CFastVB__UnpackTexels_L8A8ToFloat4", UNPACK_SIGNATURE, UNPACK_TAGS | {"cfastvb", "l8a8", "luminance", "alpha-byte", "two-byte-source"}),
    "0x00585b19": ("CFastVB__TexelUnpackProfile_005e9f9c__ctor", PROFILE_SIGNATURE, PROFILE_TAGS | {"case-0x1a", "vtable-005e9f9c"}),
    "0x00585b35": ("CFastVB__UnpackTexels_A4L4ToFloat4", UNPACK_SIGNATURE, UNPACK_TAGS | {"cfastvb", "a4l4", "luminance", "alpha-nibble", "byte-source", "nibble-lanes"}),
    "0x00585bd3": ("CFastVB__TexelUnpackProfile_scalar_deleting_dtor", DTOR_SIGNATURE, DTOR_TAGS | {"shared-profile-dtor", "flags-bit0"}),
    "0x00585bef": ("CFastVB__InitTexelUnpackVTable_005e9fac", PROFILE_SIGNATURE, PROFILE_TAGS | {"case-0x1b", "vtable-005e9fac", "current-name-retained"}),
    "0x00585c0b": ("CFastVB__UnpackTexels_L16ToFloat4", UNPACK_SIGNATURE, UNPACK_TAGS | {"cfastvb", "l16", "luminance", "alpha-one", "sixteen-bit-source"}),
    "0x00585c94": ("CFastVB__InitTexelUnpackVTable_005e9fbc", PROFILE_SIGNATURE, PROFILE_TAGS | {"case-0x1c", "vtable-005e9fbc", "current-name-retained"}),
    "0x00585cb0": ("CTexture__UnpackTexels_Signed8_8_ToFloat4_RG", UNPACK_SIGNATURE, UNPACK_TAGS | {"ctexture", "signed8-8", "rg", "signed-normal", "za-one", "two-byte-source"}),
    "0x00585d6b": ("CFastVB__TexelUnpackProfile_005e9fd0__ctor", PROFILE_SIGNATURE, PROFILE_TAGS | {"case-0x1d", "vtable-005e9fd0"}),
    "0x00585d87": ("CFastVB__TexelUnpackProfile_005e9fe0__ctor", PROFILE_SIGNATURE, PROFILE_TAGS | {"case-0x1e", "vtable-005e9fe0"}),
    "0x00585da3": ("CDXTexture__UnpackTexels_Signed5_5_A6_ToFloat4", UNPACK_SIGNATURE, UNPACK_TAGS | {"cdxtexture", "signed5-5-a6", "signed-normal", "alpha-six-bit", "sixteen-bit-source", "z-one"}),
    "0x00585e83": ("CFastVB__TexelUnpackProfile_005e9ff0__ctor", PROFILE_SIGNATURE, PROFILE_TAGS | {"case-0x1f", "vtable-005e9ff0"}),
    "0x00585e9f": ("CDXTexture__UnpackTexels_Signed8_8_A8_ToFloat4_RG", UNPACK_SIGNATURE, UNPACK_TAGS | {"cdxtexture", "signed8-8-a8", "rg", "signed-normal", "alpha-byte", "four-byte-source"}),
    "0x00585f6b": ("CFastVB__TexelUnpackProfile_005ea000__ctor", PROFILE_SIGNATURE, PROFILE_TAGS | {"case-0x20", "vtable-005ea000"}),
    "0x00585f87": ("CFastVB__TexelUnpackProfile_005ea010__ctor", PROFILE_SIGNATURE, PROFILE_TAGS | {"case-0x21", "vtable-005ea010"}),
    "0x00585fa3": ("CFastVB__UnpackTexels_Signed8_8_8_8_ToFloat4", UNPACK_SIGNATURE, UNPACK_TAGS | {"cfastvb", "signed8-8-8-8", "signed-normal", "four-byte-source", "rgba"}),
}

DOC_TOKENS = (
    "Wave673 texel unpack continuation",
    "texel-unpack-continuation-wave673",
    "0x0058577f CFastVB__TexelUnpackProfile_005e9f3c__ctor",
    "0x00585fa3 CFastVB__UnpackTexels_Signed8_8_8_8_ToFloat4",
    "0x0058609e CFastVB__TexelUnpackProfile_005ea020__ctor",
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
        require("Wave673 static read-back" in comment, f"missing Wave673 comment at {address}", failures)
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
        "apply-wave673-dry.log": "SUMMARY: updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 missing=0 bad=0",
        "apply-wave673-apply.log": "SUMMARY: updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 missing=0 bad=0",
        "apply-wave673-final-dry.log": "SUMMARY: updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=25 found=25 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=25 missing=0",
        "post-decompile.log": "targets=25 dumped=25 missing=0 failed=0",
        "post-instructions.log": "targets=25 missing=0",
        "post-xrefs.log": "Wrote 67 rows",
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
    require("test:ghidra-texel-unpack-continuation-wave673" in package.get("scripts", {}), "package script missing", failures)
    require((ROOT / "tools" / "ApplyTexelUnpackContinuationWave673.java").is_file(), "apply script missing", failures)

    docs = (PUBLIC_NOTE, FUNCTION_INDEX, TEXTURE_DOC, FASTVB_DOC, DXTEXTURE_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG)
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text, f"{token!r} missing from {path.relative_to(ROOT)}", failures)
        for token in OVERCLAIM_TOKENS:
            require(token not in text, f"overclaim token {token!r} found in {path.relative_to(ROOT)}", failures)

    for path in (LEDGER, ATTEMPT_LOG):
        text = read_text(path)
        require("Wave673 texel unpack continuation" in text, f"Wave673 missing from {path.relative_to(ROOT)}", failures)
        require("texel-unpack-continuation-wave673" in text, f"Wave673 tag missing from {path.relative_to(ROOT)}", failures)


def check_state(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("diffCount") == 0, "backup diffCount mismatch", failures)
    require(backup.get("fileCount") == 19, "backup fileCount mismatch", failures)
    require(int(float(backup.get("byteCount", 0))) == 164072327, "backup byteCount mismatch", failures)
    require("post_wave673_texel_unpack_continuation_verified" in backup.get("backupPath", ""), "backup path mismatch", failures)

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6098, "queue total mismatch", failures)
    signals = queue.get("qualitySignals", {})
    require(signals.get("commentlessFunctionCount") == 2327, "queue commentless mismatch", failures)
    require(signals.get("undefinedSignatureCount") == 1217, "queue undefined-signature mismatch", failures)
    require(signals.get("paramSignatureCount") == 546, "queue param_N mismatch", failures)
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(head.get("address") == "0x0058609e", f"queue head address mismatch: {head}", failures)
    require(head.get("name") == "CFastVB__TexelUnpackProfile_005ea020__ctor", f"queue head name mismatch: {head}", failures)

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(ledger[-1].get("task") == "Wave673 texel unpack continuation", "ledger last row mismatch", failures)
    require(attempts[-1].get("task") == "Wave673 texel unpack continuation", "attempt task mismatch", failures)
    require(attempts[-1].get("attempt_id") == 20328, "attempt id mismatch", failures)
    require(len(ledger) == 1069, "ledger row count mismatch", failures)
    require(len(attempts) == 20329, "attempt row count mismatch", failures)

    tracking = read_json(TRACKING)
    counters = tracking.get("counters", {})
    require(tracking.get("current_focus", "").startswith("Wave673 texel unpack continuation"), "tracking current_focus mismatch", failures)
    require(counters.get("ledger_rows") == 1069, "tracking ledger_rows mismatch", failures)
    require(counters.get("attempt_rows") == 20329, "tracking attempt_rows mismatch", failures)
    require(counters.get("completed") == 1060, "tracking completed mismatch", failures)
    require(counters.get("pending") == 9, "tracking pending mismatch", failures)
    require(tracking.get("next_attempt_id") == 20329, "tracking next_attempt_id mismatch", failures)

    for path in (DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        require("Wave673 texel unpack continuation" in text, f"Wave673 missing from {path.name}", failures)
        require("texel-unpack-continuation-wave673" in text, f"Wave673 tag missing from {path.name}", failures)


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
    print("Ghidra texel unpack continuation Wave673 probe")
    print(f"Status: {status}")
    print(f"Targets: {len(TARGETS)}")
    print(f"Evidence root: {BASE.relative_to(ROOT)}")
    if failures:
        for failure in failures:
            print(f"- {failure}")
    return 1 if failures and args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
