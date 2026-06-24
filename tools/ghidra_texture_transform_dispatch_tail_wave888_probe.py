#!/usr/bin/env python3
"""Validate Wave888 texture transform/dispatch read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave888-texture-transform-dispatch-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_texture_transform_dispatch_tail_wave888_2026-05-26.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
TEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "texture.cpp" / "_index.md"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
MATH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Math.cpp" / "_index.md"
VERTEX_SHADER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "VertexShader.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

TASK = "Wave888 texture transform dispatch tail"
TAG = "texture-transform-dispatch-tail-wave888"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260526-033426_post_wave888_texture_transform_dispatch_tail_verified"
STRICT_PROXY = "6052/6113 = 99.00%"
NEXT_HEAD = "0x00579a9a CVertexShader__CompileScriptWithDirectiveParser"

TARGETS = {
    "0x0057617e": ("CDXTexture__DispatchPtr00656f48_WithInit", "void CDXTexture__DispatchPtr00656f48_WithInit(void)", ("0x00656f48", "CPU-feature")),
    "0x0057618b": ("CFastVB__DispatchIndirect_00656f48", "void CFastVB__DispatchIndirect_00656f48(void)", ("0x00656f48", "no-init")),
    "0x005761f7": ("CDXTexture__DispatchPtr00657030_WithInit", "void CDXTexture__DispatchPtr00657030_WithInit(void)", ("0x00657030", "CPU-feature")),
    "0x00576286": ("CDXTexture__DispatchPtr00656f68_WithInit", "void CDXTexture__DispatchPtr00656f68_WithInit(void)", ("0x00656f68", "DATA")),
    "0x00576297": ("CDXTexture__DispatchPtr00656f68_WithInit_Thunk", "void CDXTexture__DispatchPtr00656f68_WithInit_Thunk(void)", ("0x00656f68", "no-init")),
    "0x00576404": ("Math__InterpolateVec4Cubic", "int Math__InterpolateVec4Cubic(void)", ("vec4 cubic", "RET 0x18")),
    "0x005764d5": ("CTexture__InterpolateVec4CubicNormalized_Dispatch", "int CTexture__InterpolateVec4CubicNormalized_Dispatch(void)", ("0x00657004", "RET 0x18")),
    "0x005764ff": ("Math__InterpolateVec4CubicNormalized", "int Math__InterpolateVec4CubicNormalized(void)", ("normalized vec4 cubic", "RET 0x18")),
    "0x005765f2": ("CTexture__InterpolateVec4ByUV_Dispatch", "int CTexture__InterpolateVec4ByUV_Dispatch(void)", ("0x00657008", "RET 0x18")),
    "0x00576621": ("Math__InterpolateVec4ByUV", "int Math__InterpolateVec4ByUV(void)", ("vec4 UV", "RET 0x18")),
    "0x00576698": ("CFastVB__DispatchIndirect_00656f38", "void CFastVB__DispatchIndirect_00656f38(void)", ("0x00656f38", "CVertexShader")),
    "0x005766a5": ("CVertexShader__DispatchTableCall_656f38", "void CVertexShader__DispatchTableCall_656f38(void)", ("0x00656f38", "CVertexShader")),
    "0x0057674a": ("CFastVB__DispatchIndirect_00657034", "void CFastVB__DispatchIndirect_00657034(void)", ("0x00657034", "CPU-feature")),
    "0x005768f1": ("CFastVB__DispatchIndirect_00656f3c", "void CFastVB__DispatchIndirect_00656f3c(void)", ("0x00656f3c", "matrix")),
    "0x005768fe": ("CFastVB__DispatchIndirect_00656f3c", "void CFastVB__DispatchIndirect_00656f3c(void)", ("0x00656f3c", "no-init")),
    "0x00576b3a": ("CFastVB__DispatchIndirect_00656fc4", "void CFastVB__DispatchIndirect_00656fc4(void)", ("0x00656fc4", "CVertexShader")),
    "0x00576b47": ("CVertexShader__DispatchTableCall_656fc4", "void CVertexShader__DispatchTableCall_656fc4(void)", ("0x00656fc4", "CVertexShader")),
    "0x00576dfd": ("CFastVB__DispatchIndirect_00656f78", "void CFastVB__DispatchIndirect_00656f78(void)", ("0x00656f78", "CVertexShader")),
    "0x00576e0a": ("CVertexShader__DispatchTableCall_656f78", "void CVertexShader__DispatchTableCall_656f78(void)", ("0x00656f78", "CVertexShader")),
    "0x005776d3": ("CFastVB__DispatchIndirect_00656fcc", "void CFastVB__DispatchIndirect_00656fcc(void)", ("0x00656fcc", "CPU-feature")),
    "0x005776e4": ("CFastVB__DispatchIndirect_00656fd4_ReturnInt", "int CFastVB__DispatchIndirect_00656fd4_ReturnInt(void)", ("0x00656fd4", "RET 0x14")),
    "0x0057770b": ("CFastVB__BuildTransformMatrixWithOffsets", "int CFastVB__BuildTransformMatrixWithOffsets(void)", ("quaternion rotation", "pivot", "0x006570f4")),
    "0x00577b17": ("CTexture__DispatchPtr00656f7c_WithInit", "void CTexture__DispatchPtr00656f7c_WithInit(void)", ("0x00656f7c", "CPU-feature")),
    "0x00577b24": ("CTexture__DispatchPtr00656f7c_NoInit", "void CTexture__DispatchPtr00656f7c_NoInit(void)", ("0x00656f7c", "no-init")),
    "0x00577c83": ("CTexture__DispatchPtr00656fe0_WithInit", "void CTexture__DispatchPtr00656fe0_WithInit(void)", ("0x00656fe0", "CPU-feature")),
    "0x00577c90": ("CTexture__DispatchPtr00656fe0_NoInit", "void CTexture__DispatchPtr00656fe0_NoInit(void)", ("0x00656fe0", "no-init")),
    "0x00577d47": ("CTexture__DispatchPtr0065700c_WithInit", "void CTexture__DispatchPtr0065700c_WithInit(void)", ("0x0065700c", "CPU-feature")),
    "0x00577d54": ("CTexture__DispatchPtr0065700c_NoInit", "void CTexture__DispatchPtr0065700c_NoInit(void)", ("0x0065700c", "no-init")),
    "0x00577dd5": ("CDXTexture__DispatchPtr00657010_WithInit", "void CDXTexture__DispatchPtr00657010_WithInit(void)", ("0x00657010", "CPU-feature")),
    "0x00577de2": ("CDXTexture__DispatchPtr00657010_NoInit", "void CDXTexture__DispatchPtr00657010_NoInit(void)", ("0x00657010", "no-init")),
    "0x0057800e": ("CTexture__DispatchPtr00656fe4_WithInit", "void CTexture__DispatchPtr00656fe4_WithInit(void)", ("0x00656fe4", "CPU-feature")),
    "0x005780d6": ("CDXTexture__DispatchPtr00656f84_WithInit", "void CDXTexture__DispatchPtr00656f84_WithInit(void)", ("0x00656f84", "DATA")),
    "0x005780e3": ("CDXTexture__DispatchPtr00656f84_WithInit_005780e3", "void CDXTexture__DispatchPtr00656f84_WithInit_005780e3(void)", ("0x00656f84", "no-init")),
    "0x005783d9": ("CTexture__DispatchPtr00657040_WithInit", "void CTexture__DispatchPtr00657040_WithInit(void)", ("0x00657040", "CPU-feature")),
    "0x005784a9": ("CFastVB__DispatchIndirect_00657044", "void CFastVB__DispatchIndirect_00657044(void)", ("0x00657044", "CPU-feature")),
    "0x005785c0": ("Math__TransformVec2ArrayToVec4Array", "int Math__TransformVec2ArrayToVec4Array(void)", ("strided vec2", "RET 0x18")),
    "0x005786c0": ("Math__TransformVec2ArrayByMatrixPerspective", "int Math__TransformVec2ArrayByMatrixPerspective(void)", ("perspective", "RET 0x18")),
    "0x00578794": ("Math__TransformVec2ArrayByMatrixLinear", "int Math__TransformVec2ArrayByMatrixLinear(void)", ("linear", "RET 0x18")),
    "0x00578941": ("Math__TransformVec3ArrayByMatrixPerspective", "int Math__TransformVec3ArrayByMatrixPerspective(void)", ("vec3 array", "RET 0x18")),
    "0x00578a20": ("CTexture__MapNormalizedUvToVolumeCoords", "int CTexture__MapNormalizedUvToVolumeCoords(void)", ("descriptor", "normalized UV")),
    "0x00578bad": ("CFastVB__ApplyOptionalTransformPasses_Minimal", "void CFastVB__ApplyOptionalTransformPasses_Minimal(void)", ("optional transform", "RET 0x24")),
    "0x00578dad": ("CFastVB__MapVolumeCoordsToNormalizedUv", "int CFastVB__MapVolumeCoordsToNormalizedUv(void)", ("normalized UV", "descriptor")),
    "0x00578f53": ("CFastVB__ApplyOptionalTransformPasses", "void CFastVB__ApplyOptionalTransformPasses(void)", ("optional transform", "RET 0x24")),
    "0x00579273": ("CTexture__BuildTransformMatrixWithOptionalOffsets", "int CTexture__BuildTransformMatrixWithOptionalOffsets(void)", ("quaternion rotations", "RET 0x1c")),
}

COMMON_TAGS = {
    "static-reaudit",
    TAG,
    "wave888-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-verified",
    "stack-locked-abi",
    "hidden-register-context",
    "texture-transform-dispatch-tail",
    "dispatch-table",
}

CORE_ANCHORS = (
    TASK,
    TAG,
    "0x0057617e CDXTexture__DispatchPtr00656f48_WithInit",
    "0x00576286 CDXTexture__DispatchPtr00656f68_WithInit",
    "0x00576404 Math__InterpolateVec4Cubic",
    "0x00576621 Math__InterpolateVec4ByUV",
    "0x005768fe CFastVB__DispatchIndirect_00656f3c",
    "0x0057770b CFastVB__BuildTransformMatrixWithOffsets",
    "0x00578a20 CTexture__MapNormalizedUvToVolumeCoords",
    "0x00578dad CFastVB__MapVolumeCoordsToNormalizedUv",
    "0x00578f53 CFastVB__ApplyOptionalTransformPasses",
    "0x00579273 CTexture__BuildTransformMatrixWithOptionalOffsets",
    "0x00656f48",
    "0x0065715c",
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
        "targets-snapshot.tsv": 44,
        "pre-metadata.tsv": 44,
        "pre-tags.tsv": 44,
        "pre-xrefs.tsv": 131,
        "pre-instructions.tsv": 1581,
        "pre-decompile/index.tsv": 44,
        "post-metadata.tsv": 44,
        "post-tags.tsv": 44,
        "post-xrefs.tsv": 131,
        "post-instructions.tsv": 1581,
        "post-decompile/index.tsv": 44,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, (name, signature, tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in ("Wave888 static read-back", "Static retail Ghidra evidence only", "remain unproven", *tokens):
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


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=44 renamed=0 would_rename=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=44 skipped=0 renamed=0 would_rename=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=44 renamed=0 would_rename=0 missing=0 bad=0",
        "post-metadata.log": "targets=44 found=44 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=44 missing=0",
        "post-xrefs.log": "Wrote 131 rows",
        "post-instructions.log": "Wrote 1581 function-body instruction rows",
        "post-decompile.log": "targets=44 dumped=44 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6113 commented_functions=6052",
        "queue-probe.log": "Commentless functions: 61",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave888.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave888_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "BAD:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6113, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 61, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6113, "quality TSV row count mismatch", failures)
    require(commented == 6052, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6052, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x00579a9a", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CVertexShader__CompileScriptWithDirectiveParser", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173116295 or backup.get("totalBytes") == 173116295.0, "backup byte count mismatch", failures)
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

    owner_docs = {
        DXTEXTURE_DOC: ("Wave888", TAG, "0x0057617e CDXTexture__DispatchPtr00656f48_WithInit", "0x005780d6 CDXTexture__DispatchPtr00656f84_WithInit", BACKUP_PATH),
        TEXTURE_DOC: ("Wave888", TAG, "0x00578a20 CTexture__MapNormalizedUvToVolumeCoords", "0x00579273 CTexture__BuildTransformMatrixWithOptionalOffsets", BACKUP_PATH),
        FASTVB_DOC: ("Wave888", TAG, "0x0057770b CFastVB__BuildTransformMatrixWithOffsets", "0x00578f53 CFastVB__ApplyOptionalTransformPasses", BACKUP_PATH),
        MATH_DOC: ("Wave888", TAG, "0x00576404 Math__InterpolateVec4Cubic", "0x005785c0 Math__TransformVec2ArrayToVec4Array", BACKUP_PATH),
        VERTEX_SHADER_DOC: ("Wave888", TAG, "0x005766a5 CVertexShader__DispatchTableCall_656f38", "0x00576e0a CVertexShader__DispatchTableCall_656f78", BACKUP_PATH),
    }
    for path, tokens in owner_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-texture-transform-dispatch-tail-wave888") == r"py -3 tools\ghidra_texture_transform_dispatch_tail_wave888_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave888 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20543 for row in attempts), "missing Wave888 attempt row", failures)


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
        print("Wave888 texture-transform-dispatch probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave888 texture-transform-dispatch probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
