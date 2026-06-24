#!/usr/bin/env python3
"""Validate Wave668 dither-packer head read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave668-dither-packer-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_dither_packer_head_wave668_2026-05-21.md"
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
    "dither-packer-head-wave668",
    "wave668-readback-verified",
    "static-reaudit",
    "retail-binary-evidence",
    "signature-hardened",
    "comment-hardened",
}

PACKER_SIGNATURE = "void __thiscall {name}(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)"

TARGETS = {
    "0x0058210e": {
        "name": "CTexture__PostProcessDecodedTexels_GammaOrSquare",
        "signature": "void __thiscall CTexture__PostProcessDecodedTexels_GammaOrSquare(void * this, float * texel_vec4_array, uint unused_context)",
        "tags": {"ctexture", "texel-postprocess", "gamma-or-square", "vec4"},
        "comment_tokens": ("count +0x1060", "mode +0x08", "CFastVB__LookupCurveFromSquaredInput"),
        "decompile": "0058210e_CTexture__PostProcessDecodedTexels_GammaOrSquare.c",
    },
    "0x00582244": {
        "name": "CFastVB__PackTexels_Dither_Bits8_8_8_BGR",
        "tags": {"cfastvb", "dither-packer", "bgr888", "byte-output"},
        "comment_tokens": ("0x005e9f44", "B,G,R", "+0x1058/+0x105c/+0x20"),
        "decompile": "00582244_CFastVB__PackTexels_Dither_Bits8_8_8_BGR.c",
    },
    "0x00582355": {
        "name": "CFastVB__PackTexels_Dither_Bits8_8_8_8_ARGB",
        "tags": {"cfastvb", "dither-packer", "argb8888", "dword-output"},
        "comment_tokens": ("0x005e9f54", "ARGB8888-style", "optional normalization"),
        "decompile": "00582355_CFastVB__PackTexels_Dither_Bits8_8_8_8_ARGB.c",
    },
    "0x0058249e": {
        "name": "CFastVB__PackTexels_Dither_Bits8_8_8_RGB",
        "tags": {"cfastvb", "dither-packer", "rgb888", "byte-output"},
        "comment_tokens": ("0x005e9f64", "24-bit RGB", "per-pixel dither"),
        "decompile": "0058249e_CFastVB__PackTexels_Dither_Bits8_8_8_RGB.c",
    },
    "0x005825c3": {
        "name": "CFastVB__PackTexels_Dither_Bits5_6_5",
        "tags": {"cfastvb", "dither-packer", "rgb565", "word-output"},
        "comment_tokens": ("0x005e9f74", "RGB565", "5/6/5 scale"),
        "decompile": "005825c3_CFastVB__PackTexels_Dither_Bits5_6_5.c",
    },
    "0x005826e8": {
        "name": "CFastVB__PackTexels_Dither_Bits5_5_5",
        "tags": {"cfastvb", "dither-packer", "rgb555", "word-output"},
        "comment_tokens": ("0x005e9f84", "RGB555", "5-bit scale"),
        "decompile": "005826e8_CFastVB__PackTexels_Dither_Bits5_5_5.c",
    },
    "0x0058280d": {
        "name": "CFastVB__PackTexels_Dither_A1R5G5B5",
        "tags": {"cfastvb", "dither-packer", "a1r5g5b5", "word-output"},
        "comment_tokens": ("0x005e9f94", "one-bit alpha", "A1R5G5B5-style"),
        "decompile": "0058280d_CFastVB__PackTexels_Dither_A1R5G5B5.c",
    },
    "0x00582950": {
        "name": "CFastVB__PackTexels_Dither_A4R4G4B4",
        "tags": {"cfastvb", "dither-packer", "a4r4g4b4", "word-output"},
        "comment_tokens": ("0x005e9fa4", "A4R4G4B4-style", "four nibbles"),
        "decompile": "00582950_CFastVB__PackTexels_Dither_A4R4G4B4.c",
    },
    "0x00582a99": {
        "name": "CTexture__PackTexels_Dither_Bits332",
        "tags": {"ctexture", "dither-packer", "bits332", "byte-output"},
        "comment_tokens": ("0x005e9fb4", "3-3-2", "dither table"),
        "decompile": "00582a99_CTexture__PackTexels_Dither_Bits332.c",
    },
    "0x00582bbe": {
        "name": "CTexture__PackTexels_Dither_Bits8",
        "tags": {"ctexture", "dither-packer", "bits8", "byte-output"},
        "comment_tokens": ("0x005e9fc4", "single-channel", "source lane at +0x0c"),
        "decompile": "00582bbe_CTexture__PackTexels_Dither_Bits8.c",
    },
    "0x00582c8a": {
        "name": "CTexture__PackTexels_Dither_Bits565",
        "tags": {"ctexture", "dither-packer", "bits565", "word-output"},
        "comment_tokens": ("0x005e9fd8", "5/6/5-like", "alpha/source-lane"),
        "decompile": "00582c8a_CTexture__PackTexels_Dither_Bits565.c",
    },
    "0x00582dd3": {
        "name": "CTexture__PackTexels_Dither_Bits444",
        "tags": {"ctexture", "dither-packer", "bits444", "word-output"},
        "comment_tokens": ("0x005e9fe8", "4-4-4", "packing nibbles"),
        "decompile": "00582dd3_CTexture__PackTexels_Dither_Bits444.c",
    },
}

for data in TARGETS.values():
    data.setdefault("signature", PACKER_SIGNATURE.format(name=data["name"]))

DOC_TOKENS = (
    "Wave668 dither packer head",
    "dither-packer-head-wave668",
    "0x0058210e CTexture__PostProcessDecodedTexels_GammaOrSquare",
    "0x00582dd3 CTexture__PackTexels_Dither_Bits444",
    "0x00582ef8 CDXTexture__PackTexels_Dither_Bits2_10_10_10",
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
        require("Wave668 static read-back" in comment, f"missing Wave668 comment at {address}", failures)
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
        "apply-wave668-dry.log": "SUMMARY: updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=12 missing=0 bad=0",
        "apply-wave668-apply.log": "SUMMARY: updated=12 skipped=0 renamed=0 would_rename=0 signature_updated=12 missing=0 bad=0",
        "apply-wave668-final-dry.log": "SUMMARY: updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=12 found=12 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "post-decompile.log": "targets=12 dumped=12 missing=0 failed=0",
        "post-instructions.log": "targets=12 missing=0",
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
    require("Wrote 444 instruction rows" in instructions, "instruction row count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require("test:ghidra-dither-packer-head-wave668" in package.get("scripts", {}), "package script missing", failures)
    require((ROOT / "tools" / "ApplyDitherPackerHeadWave668.java").is_file(), "apply script missing", failures)

    docs = (PUBLIC_NOTE, FUNCTION_INDEX, DXTEXTURE_DOC, FASTVB_DOC, TEXTURE_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG)
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text, f"{token!r} missing from {path.relative_to(ROOT)}", failures)
        for token in OVERCLAIM_TOKENS:
            require(token not in text, f"overclaim token {token!r} found in {path.relative_to(ROOT)}", failures)

    for path in (LEDGER, ATTEMPT_LOG):
        text = read_text(path)
        require("Wave668 dither packer head" in text, f"Wave668 missing from {path.relative_to(ROOT)}", failures)
        require("dither-packer-head-wave668" in text, f"Wave668 tag missing from {path.relative_to(ROOT)}", failures)


def check_state(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("diffCount") == 0, "backup diffCount mismatch", failures)
    require(backup.get("fileCount") == 19, "backup fileCount mismatch", failures)
    require(int(float(backup.get("byteCount", 0))) == 163744647, "backup byteCount mismatch", failures)
    require("post_wave668_dither_packer_head_verified" in backup.get("backupPath", ""), "backup path mismatch", failures)

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6098, "queue total mismatch", failures)
    signals = queue.get("qualitySignals", {})
    require(signals.get("commentlessFunctionCount") == 2397, "queue commentless mismatch", failures)
    require(signals.get("undefinedSignatureCount") == 1217, "queue undefined-signature mismatch", failures)
    require(signals.get("paramSignatureCount") == 616, "queue param_N mismatch", failures)
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(head.get("address") == "0x00582ef8", f"queue head address mismatch: {head}", failures)
    require(head.get("name") == "CDXTexture__PackTexels_Dither_Bits2_10_10_10", f"queue head name mismatch: {head}", failures)

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(ledger[-1].get("task") == "Wave668 dither packer head", "ledger last row mismatch", failures)
    require(attempts[-1].get("task") == "Wave668 dither packer head", "attempt task mismatch", failures)
    require(attempts[-1].get("attempt_id") == 20323, "attempt id mismatch", failures)
    require(len(ledger) == 1064, "ledger row count mismatch", failures)
    require(len(attempts) == 20324, "attempt row count mismatch", failures)

    tracking = read_json(TRACKING)
    counters = tracking.get("counters", {})
    require(tracking.get("current_focus", "").startswith("Wave668 dither packer head"), "tracking current_focus mismatch", failures)
    require(counters.get("ledger_rows") == 1064, "tracking ledger_rows mismatch", failures)
    require(counters.get("attempt_rows") == 20324, "tracking attempt_rows mismatch", failures)
    require(counters.get("completed") == 1055, "tracking completed mismatch", failures)
    require(counters.get("pending") == 9, "tracking pending mismatch", failures)
    require(tracking.get("next_attempt_id") == 20324, "tracking next_attempt_id mismatch", failures)

    for path in (DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        require("Wave668 dither packer head" in text, f"Wave668 missing from {path.name}", failures)
        require("dither-packer-head-wave668" in text, f"Wave668 tag missing from {path.name}", failures)


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
    print("Ghidra dither packer head Wave668 probe")
    print(f"Status: {status}")
    print(f"Targets: {len(TARGETS)}")
    print(f"Evidence root: {BASE.relative_to(ROOT)}")
    if failures:
        for failure in failures:
            print(f"- {failure}")
    return 1 if failures and args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
