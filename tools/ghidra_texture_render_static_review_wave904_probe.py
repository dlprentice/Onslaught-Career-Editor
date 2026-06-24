#!/usr/bin/env python3
"""Validate Wave904 texture/resource/decode/render static-review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave904-texture-render-static-review"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BASELINE_JSON = BASE / "texture-render-static-review-baseline.json"
FAMILY_TSV = BASE / "texture-render-family-summary.tsv"
ANCHORS_TSV = BASE / "texture-render-function-anchors.tsv"
ASSET_METRICS_TSV = BASE / "texture-render-asset-metrics.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_texture_render_static_review_wave904_2026-05-26.md"
REVIEW_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "texture-render-static-review-2026-05-26.md"
STATIC_SYSTEM_REVIEW = ROOT / "reverse-engineering" / "binary-analysis" / "static-system-review-2026-05-26.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
GAME_ASSETS_INDEX = ROOT / "reverse-engineering" / "game-assets" / "_index.md"
EXTRACTION_PIPELINE = ROOT / "reverse-engineering" / "game-assets" / "extraction-pipeline.md"
TEXTURE_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "texture.cpp" / "_index.md"
DXTEXTURE_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
VBUFFER_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "vbuffer.cpp" / "_index.md"
VBUFTEXTURE_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "vbuftexture.cpp" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
PACKAGE_JSON = ROOT / "package.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260526-101300_post_wave904_texture_render_static_review_verified"

EXPECTED_FAMILIES = {
    "CDXTexture": 366,
    "CFastVB": 347,
    "CTexture": 233,
    "CVBufTexture": 40,
    "CVBuffer": 16,
    "CIBuffer": 13,
    "CDXEngine": 60,
    "CEngine": 55,
    "CRenderQueue": 18,
    "D3DStateCache": 11,
    "RenderState": 1,
    "CVertexShader": 22,
    "CDXSurf": 13,
    "CDXMeshVB": 13,
    "CMeshRenderer": 4,
    "CFeatureTexture": 2,
    "CTextureSequence": 2,
    "CTextureBase": 1,
    "CUMTexture": 6,
    "CLandscapeTexture": 16,
    "DXParticleTexture": 9,
    "CWaterRenderSystem": 12,
    "CDXMemBuffer": 15,
    "CImageLoader": 10,
    "CTGALoader": 4,
}

EXPECTED_ASSET_METRICS = {
    "resourceArchives": "301",
    "goodieResourceArchives": "232",
    "looseTexturesExported": "847/847",
    "looseMeshesExported": "213/213",
    "embeddedMeshesExported": "139/139",
    "textRefsResolved": "601/601",
    "meshRefsResolved": "209/209",
    "gdieTextureRefsResolved": "206/206",
    "gdieMeshRefsResolved": "42/42",
    "videosInventoried": "66",
    "languageRows": "2571",
    "catalogRowsWithGoodies": "4050",
    "modelRows": "352",
    "modelRowsWithReadableMaterials": "352/352",
    "modelRowsWithTextureBindings": "352/352",
    "modelRowsWithCatalogResolvedTextureBinding": "352/352",
    "modelTextureSidecarRefs": "213/213",
}

REQUIRED_ANCHORS = {
    "CDXTexture__LoadTextureFromFile_Core",
    "CDXTexture__DecodeMemoryToTextureObject",
    "CDXTexture__DecodeFromMemory_WithFallbackCodecs",
    "CDXTexture__UploadDecodedBufferToSurface",
    "CDXTexture__ValidateJpegFrameAndComputeMcuLayout",
    "CDXTexture__ConvertYCbCrToRgb24_Mmx",
    "CTexture__FindTexture",
    "CTexture__ctor",
    "CTexture__Release",
    "CTexture__InitializeDecodePipelineFromHeader",
    "CFastVB__RenderTriangleStripImmediate",
    "CFastVB__InitDualTexelConversionPipeline",
    "CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_SIMD",
    "CVBufTexture__DrawSpriteEx",
    "CVBufTexture__Render",
    "CVBufTexture__RenderModePass",
    "CVBufTexture__RenderDynamicUnitPass",
    "CVBuffer__Create",
    "CIBuffer__CreateConfigured",
    "CRenderQueue__RenderMultipassLayerA",
    "D3DStateCache__UseDefaultRenderState",
    "CEngine__TextureFormatIndexToD3D",
    "CDXEngine__Render",
    "CVertexShader__CompileScriptWithDirectiveParser",
    "CMeshRenderer__RenderMesh",
}

CORE_ANCHORS = (
    "Wave904",
    "texture-render-static-review-wave904",
    "static-coherent texture/resource/decode/render core",
    "6113/6113 = 100.00%",
    "1289",
    "25",
    "CDXTexture",
    "366",
    "CFastVB",
    "347",
    "CTexture",
    "233",
    "CVBufTexture",
    "40",
    "CDXTexture__LoadTextureFromFile_Core",
    "CDXTexture__DecodeMemoryToTextureObject",
    "CDXTexture__ValidateJpegFrameAndComputeMcuLayout",
    "CFastVB__RenderTriangleStripImmediate",
    "CVBufTexture__DrawSpriteEx",
    "847/847",
    "352/352",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime rendering parity proven",
    "gpu upload behavior proven",
    "runtime texture decode proven",
    "native textured rendering proven",
    "all object layouts proven",
    "all systems complete",
    "every system is complete",
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


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_queue(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6113, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    for name, rows in queue["priorityQueues"].items():
        require(rows == [], f"priority queue not empty: {name}", failures)

    rows = read_tsv(QUEUE_TSV)
    require(len(rows) == 6113, "quality TSV row count mismatch", failures)
    require(all(row.get("comment", "").strip() for row in rows), "quality TSV has commentless row", failures)
    require(not any(row.get("signature", "").startswith("undefined ") for row in rows), "quality TSV has undefined signature", failures)
    require(
        not any(re.search(r"\bparam_\d+\b", row.get("signature", "")) for row in rows),
        "quality TSV has param_N signature",
        failures,
    )


def check_evidence(failures: list[str]) -> None:
    baseline = read_json(BASELINE_JSON)
    require(baseline.get("wave") == "Wave904 texture/resource/decode/render static review", "baseline wave mismatch", failures)
    require(baseline.get("tag") == "texture-render-static-review-wave904", "baseline tag mismatch", failures)
    require(baseline.get("queue", {}).get("strictCleanSignatureProxy") == "6113/6113 = 100.00%", "baseline strict proxy mismatch", failures)
    reviewed = baseline.get("reviewedFunctionRows", {})
    require(reviewed.get("families") == 25, "reviewed family count mismatch", failures)
    require(reviewed.get("functions") == 1289, "reviewed function count mismatch", failures)
    require(reviewed.get("commented") == 1289, "reviewed commented count mismatch", failures)
    require(reviewed.get("cleanSignatures") == 1289, "reviewed clean-signature count mismatch", failures)

    family_rows = {row["family"]: row for row in read_tsv(FAMILY_TSV)}
    require(len(family_rows) == len(EXPECTED_FAMILIES), "family summary row count mismatch", failures)
    for family, expected in EXPECTED_FAMILIES.items():
        row = family_rows.get(family)
        require(row is not None, f"missing family row: {family}", failures)
        if row:
            require(int(row.get("count", -1)) == expected, f"family count mismatch: {family}", failures)
            require(int(row.get("commented", -1)) == expected, f"family commented mismatch: {family}", failures)
            require(int(row.get("cleanSignatures", -1)) == expected, f"family clean-signature mismatch: {family}", failures)

    assets = {row["metric"]: row["value"] for row in read_tsv(ASSET_METRICS_TSV)}
    for metric, expected in EXPECTED_ASSET_METRICS.items():
        require(assets.get(metric) == expected, f"asset metric mismatch: {metric}", failures)

    anchors = read_tsv(ANCHORS_TSV)
    require(len(anchors) == 1289, "anchor row count mismatch", failures)
    names = {row["name"] for row in anchors}
    for name in REQUIRED_ANCHORS:
        require(name in names, f"missing anchor: {name}", failures)
    for row in anchors:
        signature = row.get("signature", "")
        require(row.get("comment", "").strip() != "", f"anchor missing comment: {row.get('name')}", failures)
        require(not signature.startswith("undefined "), f"anchor undefined signature: {row.get('name')}", failures)
        require(re.search(r"\bparam_\d+\b", signature) is None, f"anchor param_N signature: {row.get('name')}", failures)
        require(row.get("status") == "OK", f"anchor status mismatch: {row.get('name')}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173247367, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = (
        PUBLIC_NOTE,
        REVIEW_DOC,
        STATIC_SYSTEM_REVIEW,
        MAPPED_SYSTEMS,
        BINARY_INDEX,
        GAME_ASSETS_INDEX,
        EXTRACTION_PIPELINE,
        TEXTURE_INDEX,
        DXTEXTURE_INDEX,
        VBUFFER_INDEX,
        VBUFTEXTURE_INDEX,
        RE_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    )
    for path in docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-texture-render-static-review-wave904")
        == r"py -3 tools\ghidra_texture_render_static_review_wave904_probe.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_queue(failures)
    check_evidence(failures)
    check_docs(failures)

    if failures:
        print("Wave904 texture/render static-review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave904 texture/render static-review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
