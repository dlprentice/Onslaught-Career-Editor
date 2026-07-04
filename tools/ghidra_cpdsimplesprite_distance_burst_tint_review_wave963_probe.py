#!/usr/bin/env python3
"""Validate Wave963 CPDSimpleSprite distance/burst/tint read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave963-cpdsimplesprite-distance-burst-tint-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_cpdsimplesprite_distance_burst_tint_review_wave963_2026-05-28.md"
PACKAGE_JSON = ROOT / "package.json"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
PARTICLE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ParticleDescriptor.cpp" / "_index.md"
VBUFTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "vbuftexture.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUALITY_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260528-135208_post_wave963_cpdsimplesprite_distance_burst_tint_review_verified"

EXPECTED_METADATA = {
    "0x004c0c70": ("CPDSimpleSprite__EvalExpressionNode", "double __cdecl CPDSimpleSprite__EvalExpressionNode(float base_value, void * post_scale_node, void * pre_scale_node, void * pre_offset_node, void * post_offset_node, int operator_id, int output_mode, float time_scale)"),
    "0x004c14f0": ("CPDSimpleSprite__VFunc_10_004c14f0", "int __thiscall CPDSimpleSprite__VFunc_10_004c14f0(void * this, void * particle, int unused_context)"),
    "0x004c35d0": ("CEngine__ConfigureParticleBurstForDistance", "void __thiscall CEngine__ConfigureParticleBurstForDistance(void * this, void * particle, int unused_context)"),
    "0x004c5c50": ("CPDSimpleSprite__BuildUvAtlasBuckets", "void __fastcall CPDSimpleSprite__BuildUvAtlasBuckets(float unused_seed)"),
    "0x004c5d50": ("CPDSimpleSprite__ProcessAndRenderSpriteList", "void __fastcall CPDSimpleSprite__ProcessAndRenderSpriteList(void * descriptor)"),
    "0x004c7950": ("CPDSimpleSprite__EvaluateCurveDrivenScale", "double __thiscall CPDSimpleSprite__EvaluateCurveDrivenScale(void * this, void * x_value, float lifetime, float particle_context, float eval_flags)"),
    "0x004c7db0": ("CPDSimpleSprite__InitNoiseTableOnce", "void __cdecl CPDSimpleSprite__InitNoiseTableOnce(void)"),
    "0x004c8040": ("CPDSimpleSprite__VFunc_23_004c8040", "void __fastcall CPDSimpleSprite__VFunc_23_004c8040(void * descriptor)"),
    "0x004c8060": ("CEngine__ComputeSpriteTintByDistance", "int __thiscall CEngine__ComputeSpriteTintByDistance(void * this, int particle_index, int alpha_scale, float descriptor_context, float distance_context)"),
    "0x004cab30": ("Color32__LerpArgb", "int __cdecl Color32__LerpArgb(uint from_argb, uint to_argb, float t)"),
    "0x004cac40": ("Math__InvLerpClamp01", "double __cdecl Math__InvLerpClamp01(float value, float min_value, float max_value)"),
    "0x00550200": ("CVBufTexture__GetVertexPtrAt", "void __thiscall CVBufTexture__GetVertexPtrAt(void * this, int vertex_count, void * * out_vertex_ptr, int * out_start_index)"),
}

COMMENT_TOKENS = {
    "0x004c0c70": ("Wave821", "self-recursive", "x87 ST0"),
    "0x004c35d0": ("Wave462", "particle +0x80", "CParticleManager__SetParticleResource", "particle +0x88"),
    "0x004c5d50": ("Wave462", "CVBufTexture/DXParticleTexture", "quad vertices"),
    "0x004c8040": ("Wave462", "vtable slot 23", "descriptor +0x6c"),
    "0x004c8060": ("Wave462", "packed sprite tint/alpha", "distance or age fade"),
    "0x00550200": ("Wave867", "CPDSimpleSprite", "vertex_count 4"),
}

TAG_TOKENS = {
    "0x004c35d0": ("particle-sprite-render-wave462", "distance-lod", "particle-resource"),
    "0x004c8060": ("particle-sprite-render-wave462", "distance-fade", "tint"),
    "0x004c5d50": ("particle-sprite-render-wave462", "sprite-render", "vertex-emission"),
    "0x004c8040": ("particle-sprite-render-wave462", "render-dispatch", "vtable-slot-23"),
    "0x004c0c70": ("cpdsimplesprite-expression-noise-wave821", "expression-evaluator", "x87-return"),
    "0x00550200": ("cvbuftexture-cursor-wave867", "vertex-pointer-reserve", "particle-sprite"),
}

XREF_EVIDENCE = (
    ("0x004c35d0", "0x004c36d5", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x004c8060", "0x004c8a21", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x004c8060", "0x004c8b02", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x004c5d50", "0x004c8056", "CPDSimpleSprite__VFunc_23_004c8040", "UNCONDITIONAL_CALL"),
    ("0x004c7950", "0x004c74f0", "CPDSimpleSprite__ProcessAndRenderSpriteList", "UNCONDITIONAL_CALL"),
    ("0x004c7db0", "0x004c5d5e", "CPDSimpleSprite__ProcessAndRenderSpriteList", "UNCONDITIONAL_CALL"),
    ("0x00550200", "0x004c767b", "CPDSimpleSprite__ProcessAndRenderSpriteList", "UNCONDITIONAL_CALL"),
)

INSTRUCTION_EVIDENCE = (
    ("0x004c35d0", "0x004c3645", "MOV", "[ESI + 0x80], ECX"),
    ("0x004c35d0", "0x004c3665", "CALL", "0x004caed0"),
    ("0x004c35d0", "0x004c367c", "ADD", "EAX, 0x20"),
    ("0x004c35d0", "0x004c3686", "MOV", "0x3e4ccccd"),
    ("0x004c35d0", "0x004c369e", "RET", "0x4"),
    ("0x004c8060", "0x004c8088", "FIDIV", "[EDI + 0x80]"),
    ("0x004c8060", "0x004c80e7", "CALL", "0x004c10c0"),
    ("0x004c8060", "0x004c814e", "LEA", "[ESI + 0x6c]"),
    ("0x004c8060", "0x004c825a", "MOV", "[ESI + 0xa4]"),
    ("0x004c8060", "0x004c8511", "RET", "0xc"),
    ("0x004c5d50", "0x004c5d5e", "CALL", "0x004c7db0"),
    ("0x004c5d50", "0x004c5d6f", "CALL", "0x004c5c50"),
    ("0x004c5d50", "0x004c74f0", "CALL", "0x004c7950"),
    ("0x004c5d50", "0x004c767b", "CALL", "0x00550200"),
)

CORE_TOKENS = (
    "Wave963",
    "cpdsimplesprite-distance-burst-tint-review-wave963",
    "0x004c35d0 CEngine__ConfigureParticleBurstForDistance",
    "0x004c8060 CEngine__ComputeSpriteTintByDistance",
    "0x004c5d50 CPDSimpleSprite__ProcessAndRenderSpriteList",
    "0x004c8040 CPDSimpleSprite__VFunc_23_004c8040",
    "0x004c3645 MOV [ESI + 0x80], ECX",
    "0x004c3665 CALL 0x004caed0",
    "0x004c8088 FIDIV [EDI + 0x80]",
    "0x004c80e7 CALL 0x004c10c0",
    "0x004c767b CVBufTexture__GetVertexPtrAt",
    "311/1408 = 22.09%",
    "6152/6152 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime particle rendering behavior proven",
    "runtime tint behavior proven",
    "runtime burst behavior proven",
    "layout proven",
    "source-owner identity proven",
    "source-body identity proven",
    "visual output proven",
    "patching proven",
    "rebuild parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def norm(address: str) -> str:
    value = (address or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    if value in {"", "<none>", "none"}:
        return value
    return "0x" + value.zfill(8)


def contains_token(text: str, token: str) -> bool:
    stripped = text.replace("`", "")
    return token in text or token in stripped or token.replace("\\", "\\\\") in text or token.replace("\\", "\\\\") in stripped


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_counts(failures: list[str]) -> None:
    expected = {
        "metadata.tsv": 12,
        "tags.tsv": 12,
        "xrefs.tsv": 30,
        "instructions.tsv": 1260,
        "body-instructions.tsv": 3407,
        "decompile/index.tsv": 12,
    }
    for relative, count in expected.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == count, f"{relative} row count mismatch: {actual} != {count}", failures)


def check_artifacts(failures: list[str]) -> None:
    metadata = {norm(row["address"]): row for row in read_tsv(BASE / "metadata.tsv")}
    tags = {norm(row["address"]): row for row in read_tsv(BASE / "tags.tsv")}
    xrefs = read_tsv(BASE / "xrefs.tsv")
    body = read_tsv(BASE / "body-instructions.tsv")

    for address, (name, signature) in EXPECTED_METADATA.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch at {address}: {row.get('name')}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in COMMENT_TOKENS.get(address, ()):
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row:
            tag_text = tag_row.get("tags", "")
            for token in TAG_TOKENS.get(address, ()):
                require(token in tag_text, f"missing tag token at {address}: {token}", failures)

    for target, from_addr, from_name, ref_type in XREF_EVIDENCE:
        require(
            any(
                norm(row.get("target_addr", "")) == target
                and norm(row.get("from_addr", "")) == from_addr
                and row.get("from_function", "") == from_name
                and row.get("ref_type", "") == ref_type
                for row in xrefs
            ),
            f"missing xref evidence: {target} from {from_addr}",
            failures,
        )

    for target, instr_addr, mnemonic, operand_token in INSTRUCTION_EVIDENCE:
        require(
            any(
                norm(row.get("target_addr", "")) == target
                and norm(row.get("instruction_addr", "")) == instr_addr
                and row.get("mnemonic", "") == mnemonic
                and operand_token in row.get("operands", "")
                for row in body
            ),
            f"missing instruction evidence: {target} {instr_addr} {mnemonic} {operand_token}",
            failures,
        )


def check_logs(failures: list[str]) -> None:
    expected = {
        "metadata.log": "targets=12 found=12 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "xrefs.log": "Wrote 30 rows",
        "instructions.log": "Wrote 1260 instruction rows",
        "body-instructions.log": "Wrote 3407 function-body instruction rows",
        "decompile.log": "targets=12 dumped=12 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "MISSING:", "FAIL:", "missing=1", "failed=1", "bad=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6152, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUALITY_TSV)
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    require(len(rows) == 6152, "quality TSV row count mismatch", failures)
    require(commented == 6152, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6152, "strict clean-signature count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 173542279, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        NOTE,
        CAMPAIGN,
        GHIDRA_REFERENCE,
        FUNCTION_INDEX,
        PARTICLE_DOC,
        VBUFTEXTURE_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-cpdsimplesprite-distance-burst-tint-review-wave963")
        == r"py -3 tools\ghidra_cpdsimplesprite_distance_burst_tint_review_wave963_probe.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_counts(failures)
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave963 CPDSimpleSprite distance/burst/tint probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave963 CPDSimpleSprite distance/burst/tint probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
