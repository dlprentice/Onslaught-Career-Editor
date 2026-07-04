#!/usr/bin/env python3
"""Validate Wave1164 engine/render-resource current-risk evidence."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1164-engine-render-resource-current-risk-review"
FOCUSED_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.json"
RISK_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-risk-ranked-functions.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1164-engine-render-resource-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1164-engine-render-resource-current-risk-review.md"
CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "mesh-resource-render-static-contract.md"
CONTRACT_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mesh-resource-render-static-contract.md"
READINESS = ROOT / "release" / "readiness" / "wave1164_engine_render_resource_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260606-033330_post_wave1164_engine_render_resource_current_risk_review_verified"
EXPECTED_SOURCE_ROOT = str(Path.home() / "Ghidra" / "Projects")

TARGETS = {
    "0x0044a020": ("CEngine__SetViewpoint", "void __thiscall CEngine__SetViewpoint(void * this, int viewpoint, void * camera, void * viewport, void * player)", ("RET 0x10", "CInterpolatedCamera")),
    "0x0044a1c0": ("CEngine__UpdatePos", "void __thiscall CEngine__UpdatePos(void * this, void * camera)", ("render-landscape flag", "CDXLandscape__SetTileData")),
    "0x00476fe0": ("CVBufTexture__RenderDynamicUnitPass", "void CVBufTexture__RenderDynamicUnitPass(void)", ("active unit list", "CRenderQueue__InsertSortedByDepth")),
    "0x0048f5c0": ("CLevelBriefingLog__dtor", "void __thiscall CLevelBriefingLog__dtor(void * this)", ("vtable 0x005dc208", "CMonitor__Shutdown")),
    "0x0048f620": ("CLevelBriefingLog__Render", "void __thiscall CLevelBriefingLog__Render(void * this, void * viewport)", ("CDXEngine__PostRender", "GAME.GetLevelBriefingLog()->Render(viewport)")),
    "0x004911c0": ("CMapTex__LoadTexture", "int __thiscall CMapTex__LoadTexture(void * this, char * texture_path, int texture_width, int texture_index)", ("RET 0xc", "CTGALoader")),
    "0x004914b0": ("CMapTex__LoadMixerTextureSet", "int __thiscall CMapTex__LoadMixerTextureSet(void * this, int set_id, int texture_count, int texture_width)", ("texture_width * texture_width * 4 * texture_count", "CMapTex__LoadTexture")),
    "0x004901e0": ("MathMatrix3x4__AssignFromEightScalars", "void __thiscall MathMatrix3x4__AssignFromEightScalars(void * this, float scalar_00, float scalar_14, float scalar_18, float scalar_1c, float scalar_20, float scalar_24, float scalar_28, float scalar_2c)", ("RET 0x20", "CEngine__SetupLights")),
    "0x004f6fd0": ("CUnit__RenderWithDistanceFade", "bool __thiscall CUnit__RenderWithDistanceFade(void * this, uint render_flags)", ("OID__RenderWithState1BOverride", "0x0063012c")),
    "0x004fd500": ("CUnit__ApplyRenderPositionDeltaToVector", "void __thiscall CUnit__ApplyRenderPositionDeltaToVector(void * this, void * inout_position)", ("HUD target-marker", "CActor__GetRenderPos")),
    "0x00528b00": ("CEngine__InvokeCallbackIfStateMinusOne", "void __thiscall CEngine__InvokeCallbackIfStateMinusOne(void * this, int callback_value)", ("RET 0x4", "this+0x0c equals -1")),
    "0x00528b20": ("CTweakInt_SetNumViewpoints__ctor", "void * __thiscall CTweakInt_SetNumViewpoints__ctor(void * this, void * callback_context, int initial_value)", ("PTR_CEngine__SetNumViewpoints_005e4aa4", "this+0x0c")),
    "0x00541f50": ("CDXEngine__GenerateLandscapeCacheTileChunk", "void __thiscall CDXEngine__GenerateLandscapeCacheTileChunk(void * this, int detail_shift, void * source_cache_info, void * source_pixels, int tile_x, int tile_y, int dest_x, int dest_y, int tile_count_x, int tile_count_y, int output_stride_pixels)", ("RET 0x28", "ARGB cache pixels")),
    "0x00544040": ("CDXEngine__ClearKempyCubeTextureSlots", "void * __fastcall CDXEngine__ClearKempyCubeTextureSlots(void * kempy_cube_resources)", ("0xa14 block", "five 4-byte texture slots")),
    "0x00544060": ("CDXEngine__ReleaseKempyCubeTexturesAndVertexBuffer", "void __fastcall CDXEngine__ReleaseKempyCubeTexturesAndVertexBuffer(void * kempy_cube_resources)", ("CTexture__DecrementRefCountFromNameField", "0x008aa908")),
    "0x00544a00": ("CDXLandscape__Constructor", "void * __fastcall CDXLandscape__Constructor(void * this)", ("vtable 0x005e50d0", "0x40-byte object")),
    "0x00544fb0": ("CDXLandscape__ResetWrapper", "void __thiscall CDXLandscape__ResetWrapper(void * this, int reset_x, int reset_y)", ("RET 0x8", "wrapper ignores")),
    "0x00546b40": ("CDXLandscape__UpdateLOD", "void __thiscall CDXLandscape__UpdateLOD(void * this, void * engine_context_470, int record_index)", ("RET 0x8", "64x64 tile records")),
    "0x00555600": ("CAtmosphericsProfile__VFunc08_UpdateSnowAndRenderOverlay", "void __fastcall CAtmosphericsProfile__VFunc08_UpdateSnowAndRenderOverlay(void * this)", ("vtable 0x005e5974", "atm_snowdensity")),
}

DOCS = [
    NOTE,
    NOTE_MIRROR,
    CONTRACT,
    CONTRACT_MIRROR,
    READINESS,
    PROGRESS,
    PROGRESS_MIRROR,
    ROOT / "AGENTS.md",
    ROOT / "README.MD",
    ROOT / "CURRENT_CAPABILITIES.md",
    ROOT / "reverse-engineering" / "RE-INDEX.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md",
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

DOC_TOKENS = (
    "Wave1164",
    "wave1164-engine-render-resource-current-risk-review",
    "583/1179 = 49.45%",
    "19 CEngine/CDXEngine/CDXLandscape/CUnit/render-resource current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 596",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "Codex read-only consults used",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "52 xref rows",
    "3400 instruction rows",
    "CEngine__SetViewpoint",
    "CEngine__UpdatePos",
    "CVBufTexture__RenderDynamicUnitPass",
    "CMapTex__LoadTexture",
    "CMapTex__LoadMixerTextureSet",
    "CUnit__RenderWithDistanceFade",
    "CDXEngine__GenerateLandscapeCacheTileChunk",
    "CDXEngine__ReleaseKempyCubeTexturesAndVertexBuffer",
    "CDXLandscape__UpdateLOD",
    "CAtmosphericsProfile__VFunc08_UpdateSnowAndRenderOverlay",
    BACKUP,
    "mesh-resource-render-static-contract.md",
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime render behavior proven",
    "runtime landscape behavior proven",
    "runtime terrain texture behavior proven",
    "runtime atmospherics behavior proven",
    "exact layout proven",
    "source identity proven",
    "rebuild parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def normalize_address(address: str) -> str:
    value = (address or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


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
        "targets.txt": 19,
        "pre-metadata.tsv": 19,
        "pre-tags.tsv": 19,
        "pre-xrefs.tsv": 52,
        "pre-instructions.tsv": 3400,
        "pre-decompile/index.tsv": 19,
    }
    for relative, expected in expected_counts.items():
        path = BASE / relative
        count = len(read_text(path).splitlines()) if relative == "targets.txt" else len(read_tsv(path))
        require(count == expected, f"{relative} row count mismatch: {count}", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in comment_tokens:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require("static-reaudit" in actual_tags, f"static-reaudit tag missing at {address}", failures)
            require("retail-binary-evidence" in actual_tags, f"retail-binary-evidence tag missing at {address}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    ref_types = [row.get("ref_type") for row in xrefs]
    require(ref_types.count("UNCONDITIONAL_CALL") == 51, "UNCONDITIONAL_CALL xref count mismatch", failures)
    require(ref_types.count("DATA") == 1, "DATA xref count mismatch", failures)


def check_logs_backup_queue(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=19 found=19 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=19 missing=0",
        "pre-xrefs.log": "Wrote 52 rows",
        "pre-instructions.log": "Wrote 3400 function-body instruction rows",
        "pre-decompile.log": "targets=19 dumped=19 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "SCRIPT ERROR", "BADADDR", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("sourceRoot") == EXPECTED_SOURCE_ROOT, "backup source root mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 175999879, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)

    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6411, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6411, "quality TSV row count mismatch", failures)
    require(commented == 6411, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6411, "strict clean-signature count mismatch", failures)
    require(read_json(RISK_JSON).get("candidateFunctions") == 6166, "current risk candidate mismatch", failures)
    require(read_json(FOCUSED_JSON).get("candidateFunctions") == 1178, "focused candidate mismatch", failures)


def check_docs_progress(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    latest = progress.get("latestWave", {})
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(latest.get("wave") == "Wave1164 engine/render-resource current-risk review", "latest wave mismatch", failures)
    require(latest.get("tag") == "wave1164-engine-render-resource-current-risk-review", "latest tag mismatch", failures)
    require(latest.get("backup") == BACKUP, "latest backup mismatch", failures)
    require(current.get("focusedReviewed") == 583, "progress focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "49.45%", "progress focused percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 596, "progress remaining mismatch", failures)
    require(current.get("liveFocusedCandidatesAfterLatestReview") == 1178, "progress live focused mismatch", failures)
    require(current.get("latestReviewWave") == "Wave1164 engine/render-resource current-risk review", "progress latest review mismatch", failures)

    for path in DOCS:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1164 note mirror mismatch", failures)
    require(read_text(CONTRACT) == read_text(CONTRACT_MIRROR), "mesh/resource/render contract mirror mismatch", failures)
    require(read_text(PROGRESS) == read_text(PROGRESS_MIRROR), "progress mirror mismatch", failures)
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:wave1164-engine-render-resource-current-risk-review")
        == r"py -3 tools\wave1164_engine_render_resource_current_risk_review.py --check",
        "missing Wave1164 package script",
        failures,
    )
    require(
        scripts.get("test:mesh-resource-render-static-contract")
        == r"py -3 tools\mesh_resource_render_static_contract_probe.py --check",
        "missing mesh/resource/render contract package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()
    failures: list[str] = []
    check_artifacts(failures)
    check_logs_backup_queue(failures)
    check_docs_progress(failures)
    if failures:
        print("Wave1164 engine/render-resource current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1164 engine/render-resource current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
