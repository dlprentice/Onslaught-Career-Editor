#!/usr/bin/env python3
"""Validate Wave666 texture dual-profile/upload read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave666-texture-dual-profile-upload"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_texture_dual_profile_wave666_2026-05-21.md"
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
    "texture-dual-profile-wave666",
    "wave666-readback-verified",
    "static-reaudit",
    "retail-binary-evidence",
    "signature-hardened",
    "comment-hardened",
}

TARGETS = {
    "0x0057fa10": {
        "name": "CFastVB__BlendWeightTable_scalar_deleting_dtor",
        "signature": "int * __thiscall CFastVB__BlendWeightTable_scalar_deleting_dtor(void * this, uint delete_flags, int unused_context)",
        "tags": {"cfastvb", "dual-profile", "blend-weight-table", "deleting-dtor"},
        "comment_tokens": ("delete_flags bit 2", "CDXTexture__RepeatCallbackN", "allocator ownership"),
        "decompile": "0057fa10_CFastVB__BlendWeightTable_scalar_deleting_dtor.c",
    },
    "0x0057fa5c": {
        "name": "CFastVB__BlendDualProfileBoneWeights",
        "signature": "int __fastcall CFastVB__BlendDualProfileBoneWeights(void * dual_profile_context)",
        "tags": {"cfastvb", "dual-profile", "weighted-resample", "vec4-scratch"},
        "comment_tokens": ("X/Y/Z resample bucket tables", "vtable slot +4", "vtable slot +8"),
        "decompile": "0057fa5c_CFastVB__BlendDualProfileBoneWeights.c",
    },
    "0x00580120": {
        "name": "CFastVB__RunDualProfileConversionStage",
        "signature": "int __fastcall CFastVB__RunDualProfileConversionStage(void * dual_profile_context)",
        "tags": {"cfastvb", "dual-profile", "conversion-stage", "weighted-resample"},
        "comment_tokens": ("single-slice", "X/Y resample bucket tables", "runtime conversion quality"),
        "decompile": "00580120_CFastVB__RunDualProfileConversionStage.c",
    },
    "0x0058070e": {
        "name": "CFastVB__InitDualTexelConversionPipeline",
        "signature": "int __thiscall CFastVB__InitDualTexelConversionPipeline(void * this, void * source_profile_descriptor, void * destination_profile_descriptor, int conversion_flags, uint unused_context)",
        "tags": {"cfastvb", "dual-profile", "texel-unpack", "conversion-dispatch"},
        "comment_tokens": ("creates paired texel-unpack profiles", "direct copy/resample/downsample helpers", "profile ABI"),
        "decompile": "0058070e_CFastVB__InitDualTexelConversionPipeline.c",
    },
    "0x0058083d": {
        "name": "CDXTexture__ResetSurfaceCopyContext",
        "signature": "void __fastcall CDXTexture__ResetSurfaceCopyContext(void * surface_copy_context)",
        "tags": {"cdxtexture", "surface-copy", "upload-context", "context-reset"},
        "comment_tokens": ("five consecutive dwords", "surface-copy/upload context", "runtime upload behavior"),
        "decompile": "0058083d_CDXTexture__ResetSurfaceCopyContext.c",
    },
    "0x00580850": {
        "name": "CDXTexture__CopyLockedRectPitchAware",
        "signature": "int __stdcall CDXTexture__CopyLockedRectPitchAware(void * source_surface, void * destination_surface)",
        "tags": {"cdxtexture", "surface-copy", "locked-rect", "pitch-aware", "dxt"},
        "comment_tokens": ("DXT1-DXT5", "min(source_pitch,destination_pitch)", "runtime copy fidelity"),
        "decompile": "00580850_CDXTexture__CopyLockedRectPitchAware.c",
    },
    "0x0058092d": {
        "name": "CDXTexture__FinalizeTextureUploadAndReleaseTemp",
        "signature": "int __fastcall CDXTexture__FinalizeTextureUploadAndReleaseTemp(void * upload_context)",
        "tags": {"cdxtexture", "surface-upload", "release-temp", "fallback-copy"},
        "comment_tokens": ("device vtable +0x78", "CDXTexture__CopyLockedRectPitchAware", "UpdateSurface identity"),
        "decompile": "0058092d_CDXTexture__FinalizeTextureUploadAndReleaseTemp.c",
    },
    "0x005809de": {
        "name": "CFastVB__ShutdownActiveProfile",
        "signature": "int __fastcall CFastVB__ShutdownActiveProfile(void * active_profile_slot)",
        "tags": {"cfastvb", "profile-lifetime", "active-profile", "release"},
        "comment_tokens": ("vtable slot +0x28", "vtable slot +0x08", "runtime profile lifetime"),
        "decompile": "005809de_CFastVB__ShutdownActiveProfile.c",
    },
    "0x00580a00": {
        "name": "CDXTexture__FinalizeTextureUploadAndReleaseTemp_Duplicate",
        "signature": "int __fastcall CDXTexture__FinalizeTextureUploadAndReleaseTemp_Duplicate(void * upload_context)",
        "tags": {"cdxtexture", "surface-upload", "release-temp", "duplicate-entry"},
        "comment_tokens": ("duplicate/tail entry", "pitch-aware fallback copy", "runtime upload behavior"),
        "decompile": "00580a00_CDXTexture__FinalizeTextureUploadAndReleaseTemp_Duplicate.c",
    },
    "0x00580eef": {
        "name": "CFastVB__ShutdownActiveProfile_Thunk",
        "signature": "int __fastcall CFastVB__ShutdownActiveProfile_Thunk(void * active_profile_slot)",
        "tags": {"cfastvb", "profile-lifetime", "active-profile", "thunk"},
        "comment_tokens": ("thunk/alias entry", "vtable slot +0x28", "retained CFastVB owner label"),
        "decompile": "00580eef_CFastVB__ShutdownActiveProfile_Thunk.c",
    },
}

DOC_TOKENS = (
    "Wave666 texture dual-profile/upload",
    "texture-dual-profile-wave666",
    "0x0057fa10 CFastVB__BlendWeightTable_scalar_deleting_dtor",
    "0x00580eef CFastVB__ShutdownActiveProfile_Thunk",
    "0x00581263 CFastVB__TexelUnpackProfile__dtor",
)

OVERCLAIM_TOKENS = (
    "fully reverse-engineered",
    "fully recovered",
    "runtime texture conversion behavior proven",
    "runtime upload behavior proven",
    "runtime blend quality proven",
    "exact profile layout proven",
    "exact descriptor layout proven",
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
        require("Wave666 static read-back" in comment, f"missing Wave666 comment at {address}", failures)
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
        "apply-wave666-dry.log": "SUMMARY: updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=10 missing=0 bad=0",
        "apply-wave666-apply.log": "SUMMARY: updated=10 skipped=0 renamed=0 would_rename=0 signature_updated=8 missing=0 bad=0",
        "apply-wave666-final-dry.log": "SUMMARY: updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=10 found=10 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "post-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "post-instructions.log": "targets=10 missing=0",
        "post-xrefs.log": "Wrote 22 rows",
    }
    for filename, token in expected_exact.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"save report missing in {filename}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("ERROR REPORT SCRIPT ERROR" not in text, f"script error found in {filename}", failures)
        require("BAD:" not in text and "BADNAME:" not in text and "MISSING:" not in text, f"bad/missing marker found in {filename}", failures)

    instructions = read_text(BASE / "post-instructions.log")
    require("Wrote 1060 instruction rows" in instructions, "instruction row count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require("test:ghidra-texture-dual-profile-wave666" in package.get("scripts", {}), "package script missing", failures)

    for path in (PUBLIC_NOTE, FUNCTION_INDEX, DXTEXTURE_DOC, FASTVB_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG):
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text, f"{token!r} missing from {path.relative_to(ROOT)}", failures)
        for token in OVERCLAIM_TOKENS:
            require(token not in text, f"overclaim token {token!r} found in {path.relative_to(ROOT)}", failures)

    for path in (LEDGER, ATTEMPT_LOG):
        text = read_text(path)
        require("Wave666 texture dual-profile/upload" in text, f"Wave666 missing from {path.relative_to(ROOT)}", failures)
        require("texture-dual-profile-wave666" in text, f"Wave666 tag missing from {path.relative_to(ROOT)}", failures)


def check_state(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("diffCount") == 0, "backup diffCount mismatch", failures)
    require(backup.get("fileCount") == 19, "backup fileCount mismatch", failures)
    require(int(float(backup.get("byteCount", 0))) == 163613575, "backup byteCount mismatch", failures)
    require("post_wave666_texture_dual_profile_verified" in backup.get("backupPath", ""), "backup path mismatch", failures)

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6098, "queue total mismatch", failures)
    signals = queue.get("qualitySignals", {})
    require(signals.get("commentlessFunctionCount") == 2419, "queue commentless mismatch", failures)
    require(signals.get("undefinedSignatureCount") == 1217, "queue undefined-signature mismatch", failures)
    require(signals.get("paramSignatureCount") == 638, "queue param_N mismatch", failures)
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(head.get("address") == "0x00581263", f"queue head address mismatch: {head}", failures)
    require(head.get("name") == "CFastVB__TexelUnpackProfile__dtor", f"queue head name mismatch: {head}", failures)

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(ledger[-1].get("task") == "Wave666 texture dual-profile/upload", "ledger last row mismatch", failures)
    require(attempts[-1].get("task") == "Wave666 texture dual-profile/upload", "attempt task mismatch", failures)
    require(attempts[-1].get("attempt_id") == 20321, "attempt id mismatch", failures)
    require(len(ledger) == 1062, "ledger row count mismatch", failures)
    require(len(attempts) == 20322, "attempt row count mismatch", failures)

    tracking = read_json(TRACKING)
    counters = tracking.get("counters", {})
    require(tracking.get("current_focus", "").startswith("Wave666 texture dual-profile/upload"), "tracking current_focus mismatch", failures)
    require(counters.get("ledger_rows") == 1062, "tracking ledger_rows mismatch", failures)
    require(counters.get("attempt_rows") == 20322, "tracking attempt_rows mismatch", failures)
    require(counters.get("completed") == 1053, "tracking completed mismatch", failures)
    require(counters.get("pending") == 9, "tracking pending mismatch", failures)
    require(tracking.get("next_attempt_id") == 20322, "tracking next_attempt_id mismatch", failures)

    for path in (DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        require("Wave666 texture dual-profile/upload" in text, f"Wave666 missing from {path.name}", failures)
        require("texture-dual-profile-wave666" in text, f"Wave666 tag missing from {path.name}", failures)


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
    print("Ghidra texture dual-profile/upload Wave666 probe")
    print(f"Status: {status}")
    print(f"Targets: {len(TARGETS)}")
    print(f"Evidence root: {BASE.relative_to(ROOT)}")
    if failures:
        for failure in failures:
            print(f"- {failure}")
    return 1 if failures and args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
