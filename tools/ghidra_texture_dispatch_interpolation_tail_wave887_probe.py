#!/usr/bin/env python3
"""Validate Wave887 texture dispatch/interpolation read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave887-texture-dispatch-interpolation-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_texture_dispatch_interpolation_tail_wave887_2026-05-26.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
TEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "texture.cpp" / "_index.md"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
MATH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Math.cpp" / "_index.md"
VBUFTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "vbuftexture.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

TASK = "Wave887 texture dispatch/interpolation tail"
TAG = "texture-dispatch-interpolation-tail-wave887"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260526-030217_post_wave887_texture_dispatch_interpolation_tail_verified"
STRICT_PROXY = "6008/6113 = 98.28%"
NEXT_HEAD = "0x0057617e CDXTexture__DispatchPtr00656f48_WithInit"

TARGETS = {
    "0x005759b6": ("CFastVB__DispatchIndirect_00657014", "void CFastVB__DispatchIndirect_00657014(void)", ("DAT_00657014", "CDXTexture__PackTexels_DispatchIndirect_005759c3")),
    "0x005759c3": ("CDXTexture__PackTexels_DispatchIndirect_005759c3", "void CDXTexture__PackTexels_DispatchIndirect_005759c3(void)", ("0x00657014", "CDXTexture__PackTexels_CallbackPerTexel_RepeatA")),
    "0x00575a58": ("CFastVB__DispatchIndirect_00657018", "void CFastVB__DispatchIndirect_00657018(void)", ("DAT_00657018", "CDXTexture__UnpackTexels_DispatchIndirect_00575a65")),
    "0x00575a65": ("CDXTexture__UnpackTexels_DispatchIndirect_00575a65", "void CDXTexture__UnpackTexels_DispatchIndirect_00575a65(void)", ("0x00657018", "CDXTexture__UnpackTexels_CallbackPerTexel_Stride2_SetRGBAOne")),
    "0x00575b1d": ("CTexture__InterpolateVec2Cubic_Dispatch", "int CTexture__InterpolateVec2Cubic_Dispatch(void)", ("0x00656f74", "RET 0x18")),
    "0x00575b47": ("Math__InterpolateVec2Cubic", "int Math__InterpolateVec2Cubic(void)", ("vec2 cubic", "RET 0x18")),
    "0x00575bd5": ("CTexture__InterpolateVec2CubicNormalized_Dispatch", "int CTexture__InterpolateVec2CubicNormalized_Dispatch(void)", ("0x00656fec", "RET 0x18")),
    "0x00575bff": ("Math__InterpolateVec2CubicNormalized", "int Math__InterpolateVec2CubicNormalized(void)", ("normalized vec2 cubic", "RET 0x18")),
    "0x00575cae": ("CFastVB__DispatchIndirect_00656ff0_ReturnInt", "int CFastVB__DispatchIndirect_00656ff0_ReturnInt(void)", ("0x00656ff0", "RET 0x18")),
    "0x00575cdd": ("Math__InterpolateVec2ByUV", "int Math__InterpolateVec2ByUV(void)", ("vec2 bilinear/UV", "RET 0x18")),
    "0x00575d20": ("CDXTexture__DispatchPtr00656f30_WithInit", "void CDXTexture__DispatchPtr00656f30_WithInit(void)", ("0x00656f30", "CFastVB__DispatchIndirect_00656f30")),
    "0x00575d2d": ("CFastVB__DispatchIndirect_00656f30", "void CFastVB__DispatchIndirect_00656f30(void)", ("0x00656f30", "TransformVec4BatchW")),
    "0x00575d44": ("CDXTexture__DispatchPtr00656f54_WithInit", "void CDXTexture__DispatchPtr00656f54_WithInit(void)", ("0x00656f54", "CFastVB__DispatchIndirect_00656f54")),
    "0x00575d51": ("CFastVB__DispatchIndirect_00656f54", "void CFastVB__DispatchIndirect_00656f54(void)", ("0x00656f54", "TransformProjectVec4Batch")),
    "0x00575d68": ("CMeshCollisionVolume__DispatchPtr00656f44_WithInit", "void CMeshCollisionVolume__DispatchPtr00656f44_WithInit(void)", ("0x00656f44", "CFastVB__DispatchIndirect_00656f44")),
    "0x00575d75": ("CFastVB__DispatchIndirect_00656f44", "void CFastVB__DispatchIndirect_00656f44(void)", ("0x00656f44", "TransformVec4Batch_NoOffset")),
    "0x00575d8c": ("CDXTexture__DispatchPtr00656f4c_WithInit", "void CDXTexture__DispatchPtr00656f4c_WithInit(void)", ("0x00656f4c", "Runtime__CallIndirectThunk_00575d99")),
    "0x00575d99": ("Runtime__CallIndirectThunk_00575d99", "void Runtime__CallIndirectThunk_00575d99(void)", ("0x00656f4c", "Math__BuildAxisAngleRotationMatrix")),
    "0x00575dc9": ("CFastVB__HermiteInterpolateVec3", "int CFastVB__HermiteInterpolateVec3(void)", ("vec3 cubic/Hermite", "RET 0x18")),
    "0x00575e77": ("CTexture__InterpolateVec3CubicNormalized_Dispatch", "int CTexture__InterpolateVec3CubicNormalized_Dispatch(void)", ("0x00656ff8", "RET 0x18")),
    "0x00575ea1": ("Math__InterpolateVec3CubicNormalized", "int Math__InterpolateVec3CubicNormalized(void)", ("normalized vec3 cubic", "RET 0x18")),
    "0x00575f72": ("CTexture__InterpolateVec3ByUV_Dispatch", "int CTexture__InterpolateVec3ByUV_Dispatch(void)", ("0x00656ffc", "RET 0x18")),
    "0x00575fa1": ("Math__InterpolateVec3ByUV", "int Math__InterpolateVec3ByUV(void)", ("vec3 UV interpolation", "RET 0x18")),
    "0x00575ffe": ("CTexture__DispatchPtr00656f34_WithInit", "void CTexture__DispatchPtr00656f34_WithInit(void)", ("0x00656f34", "CVBufTexture__DispatchTextureTransformThunk")),
    "0x0057600b": ("CVBufTexture__DispatchTextureTransformThunk", "void CVBufTexture__DispatchTextureTransformThunk(void)", ("0x00656f34", "CVBufTexture__RenderDynamicUnitPass")),
    "0x0057609c": ("CFastVB__DispatchIndirect_00657028", "void CFastVB__DispatchIndirect_00657028(void)", ("0x00657028", "tail-jumps")),
    "0x00576154": ("CFastVB__DispatchIndirect_00656f58", "void CFastVB__DispatchIndirect_00656f58(void)", ("0x00656f58", "CFastVB__DispatchIndirectByGlobalTable")),
    "0x00576161": ("CFastVB__DispatchIndirectByGlobalTable", "void CFastVB__DispatchIndirectByGlobalTable(void)", ("0x00656f58", "CMeshRenderer__RenderMeshCore")),
    "0x00576167": ("CTexture__DispatchPtr0065702c_WithInit", "void CTexture__DispatchPtr0065702c_WithInit(void)", ("0x0065702c", "CTexture__DispatchPtr0065702c_NoInit")),
    "0x00576178": ("CTexture__DispatchPtr0065702c_NoInit", "void CTexture__DispatchPtr0065702c_NoInit(void)", ("0x0065702c", "CFastVB__ApplyOptionalTransformPasses")),
}

COMMON_TAGS = {
    "static-reaudit",
    TAG,
    "wave887-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-verified",
    "stack-locked-abi",
    "hidden-register-context",
    "texture-dispatch-interpolation-tail",
    "dispatch-table",
}

CORE_ANCHORS = (
    TASK,
    TAG,
    "0x005759b6 CFastVB__DispatchIndirect_00657014",
    "0x005759c3 CDXTexture__PackTexels_DispatchIndirect_005759c3",
    "0x00575b47 Math__InterpolateVec2Cubic",
    "0x00575dc9 CFastVB__HermiteInterpolateVec3",
    "0x0057600b CVBufTexture__DispatchTextureTransformThunk",
    "0x00576161 CFastVB__DispatchIndirectByGlobalTable",
    "0x00657014",
    "0x00656f58",
    NEXT_HEAD,
    STRICT_PROXY,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
    "dispatch-table slot targets proven",
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


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict_clean


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 30,
        "pre-tags.tsv": 30,
        "pre-xrefs.tsv": 72,
        "pre-instructions.tsv": 470,
        "pre-decompile/index.tsv": 30,
        "post-metadata.tsv": 30,
        "post-tags.tsv": 30,
        "post-xrefs.tsv": 72,
        "post-instructions.tsv": 470,
        "post-decompile/index.tsv": 30,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    instructions = read_tsv(BASE / "post-instructions.tsv")

    for address, (name, signature, tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            require("Wave887 static read-back" in comment, f"missing Wave887 comment token at {address}", failures)
            require("Static retail Ghidra evidence only" in comment, f"missing boundary token at {address}", failures)
            for token in tokens:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    by_addr = {}
    for row in instructions:
        by_addr.setdefault(normalize_address(row["target_addr"]), []).append(row)
    for address in ("0x00575b47", "0x00575cdd", "0x00575dc9", "0x00575fa1"):
        require(any(row.get("mnemonic") == "RET" and row.get("operands") == "0x18" for row in by_addr.get(address, [])), f"missing RET 0x18 at {address}", failures)
    for address in ("0x005759b6", "0x005759c3", "0x0057600b", "0x00576161"):
        require(any(row.get("mnemonic") == "JMP" and "ptr" in row.get("operands", "") for row in by_addr.get(address, [])), f"missing computed JMP at {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=30 renamed=0 would_rename=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=30 skipped=0 renamed=0 would_rename=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=30 renamed=0 would_rename=0 missing=0 bad=0",
        "post-metadata.log": "targets=30 found=30 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=30 missing=0",
        "post-xrefs.log": "Wrote 72 rows",
        "post-instructions.log": "Wrote 470 function-body instruction rows",
        "post-decompile.log": "targets=30 dumped=30 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6113 commented_functions=6008",
        "queue-probe.log": "Commentless functions: 105",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave887.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave887_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "Input file not found", "Script not found", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6113, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 105, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6113, "quality TSV row count mismatch", failures)
    require(commented == 6008, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6008, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0057617e", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CDXTexture__DispatchPtr00656f48_WithInit", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 172952455, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DXTEXTURE_DOC,
        TEXTURE_DOC,
        FASTVB_DOC,
        MATH_DOC,
        VBUFTEXTURE_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-texture-dispatch-interpolation-tail-wave887") == r"py -3 tools\ghidra_texture_dispatch_interpolation_tail_wave887_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave887 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20542 for row in attempts), "missing Wave887 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave887 texture dispatch/interpolation probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave887 texture dispatch/interpolation probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
