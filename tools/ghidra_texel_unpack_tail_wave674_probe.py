#!/usr/bin/env python3
"""Validate Wave674 texel unpack tail read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave674-texel-unpack-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_texel_unpack_tail_wave674_2026-05-21.md"
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

BASE_TAGS = {
    "static-reaudit",
    "texel-unpack-tail-wave674",
    "wave674-readback-verified",
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

TARGETS = {
    "0x0058609e": ("CFastVB__TexelUnpackProfile_005ea020__ctor", PROFILE_SIGNATURE, PROFILE_TAGS | {"vtable-005ea020"}),
    "0x005860ba": ("CTexture__UnpackTexels_Signed16_16_ToFloat4_RG", UNPACK_SIGNATURE, UNPACK_TAGS | {"ctexture", "signed16-16"}),
    "0x0058617c": ("CFastVB__InitTexelUnpackVTable_005ea034", PROFILE_SIGNATURE, PROFILE_TAGS | {"vtable-005ea034"}),
    "0x00586198": ("CFastVB__TexelUnpackProfile_005ea044__ctor", PROFILE_SIGNATURE, PROFILE_TAGS | {"vtable-005ea044"}),
    "0x005861b4": ("CDXTexture__UnpackTexels_Signed2_10_10_10_ToFloat4", UNPACK_SIGNATURE, UNPACK_TAGS | {"cdxtexture", "signed2-10-10-10"}),
    "0x005862cd": ("CFastVB__TexelUnpackProfile_005ea058__ctor", PROFILE_SIGNATURE, PROFILE_TAGS | {"vtable-005ea058"}),
    "0x005862e9": ("CFastVB__InitTexelUnpackVTable_005ea068", PROFILE_SIGNATURE, PROFILE_TAGS | {"vtable-005ea068"}),
    "0x00586305": ("CDXTexture__UnpackTexels_Signed16_16_16_16_ToFloat4", UNPACK_SIGNATURE, UNPACK_TAGS | {"cdxtexture", "signed16-16-16-16"}),
    "0x0058641c": ("CFastVB__TexelUnpackProfile_005ea078__ctor", PROFILE_SIGNATURE, PROFILE_TAGS | {"vtable-005ea078"}),
    "0x00586438": ("CTexture__UnpackTexels_NormalXY_Signed8_8_ReconstructZ", UNPACK_SIGNATURE, UNPACK_TAGS | {"ctexture", "normalxy"}),
    "0x00586519": ("CFastVB__TexelUnpackProfile_005ea088__ctor", PROFILE_SIGNATURE, PROFILE_TAGS | {"vtable-005ea088"}),
    "0x00586535": ("CFastVB__TexelUnpackProfile_005ea098__ctor", PROFILE_SIGNATURE, PROFILE_TAGS | {"vtable-005ea098"}),
    "0x00586551": ("CFastVB__TexelUnpackProfile_005ea0a8__ctor", PROFILE_SIGNATURE, PROFILE_TAGS | {"vtable-005ea0a8"}),
    "0x005865ed": ("CFastVB__TexelUnpackProfile_005ea0b8__ctor", PROFILE_SIGNATURE, PROFILE_TAGS | {"vtable-005ea0b8"}),
    "0x00586609": ("CDXTexture__UnpackTexels_CallbackPerTexel_Stride2_SetRGBAOne", UNPACK_SIGNATURE, UNPACK_TAGS | {"cdxtexture", "callback-dispatch"}),
    "0x0058669a": ("CFastVB__InitTexelUnpackVTable_005ea0c8", PROFILE_SIGNATURE, PROFILE_TAGS | {"vtable-005ea0c8"}),
    "0x005866b6": ("CFastVB__InitTexelUnpackVTable_005ea0d8", PROFILE_SIGNATURE, PROFILE_TAGS | {"vtable-005ea0d8"}),
    "0x005866d2": ("CFastVB__UnpackTexels_CallbackPerTexel_Stride4_SetZAOne", UNPACK_SIGNATURE, UNPACK_TAGS | {"cfastvb", "callback-dispatch"}),
    "0x0058675f": ("CFastVB__InitTexelUnpackVTable_005ea0e8", PROFILE_SIGNATURE, PROFILE_TAGS | {"vtable-005ea0e8"}),
    "0x0058677b": ("CDXTexture__UnpackTexels_CallbackSingleTexel", UNPACK_SIGNATURE, UNPACK_TAGS | {"cdxtexture", "single-texel"}),
    "0x005867d2": ("CFastVB__TexelUnpackProfile_005ea0f8__ctor", PROFILE_SIGNATURE, PROFILE_TAGS | {"vtable-005ea0f8"}),
    "0x0058686f": ("CTexture__UnpackTexels_CopyRaw128", UNPACK_SIGNATURE, UNPACK_TAGS | {"ctexture", "copy-raw128"}),
    "0x005868d1": ("CFastVB__UnpackTexels_L16A16_ToFloat4", UNPACK_SIGNATURE, UNPACK_TAGS | {"cfastvb", "l16a16"}),
    "0x00586978": ("CFastVB__TexelUnpackProfile_005ea108__ctor", PROFILE_SIGNATURE, PROFILE_TAGS | {"vtable-005ea108"}),
    "0x00586994": ("CFastVB__InitTexelUnpackVTable_005ea118", PROFILE_SIGNATURE, PROFILE_TAGS | {"vtable-005ea118"}),
}

DOC_TOKENS = (
    "Wave674 texel unpack tail",
    "texel-unpack-tail-wave674",
    "0x0058609e CFastVB__TexelUnpackProfile_005ea020__ctor",
    "0x00586994 CFastVB__InitTexelUnpackVTable_005ea118",
    "0x005869b0 CTexture__UnpackTexels_Bits16_16_16_ToFloat4",
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
        require("Wave674 static read-back" in comment, f"missing Wave674 comment at {address}", failures)
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
        "apply-wave674-dry.log": "SUMMARY: updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 missing=0 bad=0",
        "apply-wave674-apply.log": "SUMMARY: updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 missing=0 bad=0",
        "apply-wave674-final-dry.log": "SUMMARY: updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=25 found=25 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=25 missing=0",
        "post-decompile.log": "targets=25 dumped=25 missing=0 failed=0",
        "post-instructions.log": "targets=25 missing=0",
        "post-xrefs.log": "Wrote 25 rows",
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
    require("test:ghidra-texel-unpack-tail-wave674" in package.get("scripts", {}), "package script missing", failures)
    require((ROOT / "tools" / "ApplyTexelUnpackTailWave674.java").is_file(), "apply script missing", failures)

    docs = (PUBLIC_NOTE, FUNCTION_INDEX, TEXTURE_DOC, FASTVB_DOC, DXTEXTURE_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG)
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text, f"{token!r} missing from {path.relative_to(ROOT)}", failures)
        for token in OVERCLAIM_TOKENS:
            require(token not in text, f"overclaim token {token!r} found in {path.relative_to(ROOT)}", failures)

    for path in (LEDGER, ATTEMPT_LOG):
        text = read_text(path)
        require("Wave674 texel unpack tail" in text, f"Wave674 missing from {path.relative_to(ROOT)}", failures)
        require("texel-unpack-tail-wave674" in text, f"Wave674 tag missing from {path.relative_to(ROOT)}", failures)


def check_state(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("diffCount") == 0, "backup diffCount mismatch", failures)
    require(backup.get("fileCount") == 19, "backup fileCount mismatch", failures)
    require(int(float(backup.get("byteCount", 0))) == 164236167, "backup byteCount mismatch", failures)
    require("post_wave674_texel_unpack_tail_verified" in backup.get("backupPath", ""), "backup path mismatch", failures)

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6098, "queue total mismatch", failures)
    signals = queue.get("qualitySignals", {})
    require(signals.get("commentlessFunctionCount") == 2302, "queue commentless mismatch", failures)
    require(signals.get("undefinedSignatureCount") == 1217, "queue undefined-signature mismatch", failures)
    require(signals.get("paramSignatureCount") == 521, "queue param_N mismatch", failures)
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(head.get("address") == "0x005869b0", f"queue head address mismatch: {head}", failures)
    require(head.get("name") == "CTexture__UnpackTexels_Bits16_16_16_ToFloat4", f"queue head name mismatch: {head}", failures)

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(ledger[-1].get("task") == "Wave674 texel unpack tail", "ledger last row mismatch", failures)
    require(attempts[-1].get("task") == "Wave674 texel unpack tail", "attempt task mismatch", failures)
    require(attempts[-1].get("attempt_id") == 20329, "attempt id mismatch", failures)
    require(len(ledger) == 1070, "ledger row count mismatch", failures)
    require(len(attempts) == 20330, "attempt row count mismatch", failures)

    tracking = read_json(TRACKING)
    counters = tracking.get("counters", {})
    require(tracking.get("current_focus", "").startswith("Wave674 texel unpack tail"), "tracking current_focus mismatch", failures)
    require(counters.get("ledger_rows") == 1070, "tracking ledger_rows mismatch", failures)
    require(counters.get("attempt_rows") == 20330, "tracking attempt_rows mismatch", failures)
    require(counters.get("completed") == 1061, "tracking completed mismatch", failures)
    require(counters.get("pending") == 9, "tracking pending mismatch", failures)
    require(tracking.get("next_attempt_id") == 20330, "tracking next_attempt_id mismatch", failures)

    for path in (DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        require("Wave674 texel unpack tail" in text, f"Wave674 missing from {path.name}", failures)
        require("texel-unpack-tail-wave674" in text, f"Wave674 tag missing from {path.name}", failures)


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
    print("Ghidra texel unpack tail Wave674 probe")
    print(f"Status: {status}")
    print(f"Targets: {len(TARGETS)}")
    print(f"Evidence root: {BASE.relative_to(ROOT)}")
    if failures:
        for failure in failures:
            print(f"- {failure}")
    return 1 if failures and args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
