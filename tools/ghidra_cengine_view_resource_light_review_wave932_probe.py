#!/usr/bin/env python3
"""Validate Wave932 CEngine view/resource/light read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave932-cengine-view-resource-light-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_cengine_view_resource_light_review_wave932_2026-05-28.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
PACKAGE_JSON = ROOT / "package.json"
STATE_FILES = [
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260528-001551_post_wave932_cengine_view_resource_light_review_verified"
SCRIPT_NAME = "test:ghidra-cengine-view-resource-light-review-wave932"
SCRIPT_VALUE = r"py -3 tools\ghidra_cengine_view_resource_light_review_wave932_probe.py --check"

TARGETS = {
    "0x00449ef0": ("CEngine__GetViewMatrixFromCamera", "void __thiscall CEngine__GetViewMatrixFromCamera(void * this, void * camera, void * outViewMatrix)"),
    "0x0044a0d0": ("CEngine__SelectViewpoint", "void __thiscall CEngine__SelectViewpoint(void * this, int viewpoint)"),
    "0x0044a110": ("CEngine__ResetPos", "void __thiscall CEngine__ResetPos(void * this, int x, int y)"),
    "0x0044a130": ("CEngine__InitDamageSystem", "void __fastcall CEngine__InitDamageSystem(void * engine)"),
    "0x0044a1f0": ("CEngine__LoadMixers", "void __thiscall CEngine__LoadMixers(void * this, int set)"),
    "0x0044a2a0": ("CEngine__SetKempyCube", "void __thiscall CEngine__SetKempyCube(void * this, int number)"),
    "0x0044a2c0": ("CEngine__SetWater", "void __thiscall CEngine__SetWater(void * this, int number)"),
    "0x0044a2d0": ("CEngine__SetupLights", "void CEngine__SetupLights(void)"),
}

CONTEXT_TARGETS = {
    "0x0044a020": ("CEngine__SetViewpoint", "void __thiscall CEngine__SetViewpoint(void * this, int viewpoint, void * camera, void * viewport, void * player)"),
    "0x0044a1c0": ("CEngine__UpdatePos", "void __thiscall CEngine__UpdatePos(void * this, void * camera)"),
    "0x00491060": ("CHeightField__DeserializeMapAndInitResources", "void __thiscall CHeightField__DeserializeMapAndInitResources(void * this, void * chunk_reader)"),
    "0x0044a6e0": ("CEngine__Deserialize", "void __thiscall CEngine__Deserialize(void * this, void * chunkReader)"),
    "0x0053e2e0": ("CDXEngine__Render", "int __thiscall CDXEngine__Render(void * this, uint viewpoint)"),
    "0x005441a0": ("CDXEngine__InitKempyCubeResources", "void __thiscall CDXEngine__InitKempyCubeResources(void * this, int cube_index)"),
    "0x00544fb0": ("CDXLandscape__ResetWrapper", "void __thiscall CDXLandscape__ResetWrapper(void * this, int reset_x, int reset_y)"),
    "0x0055b330": ("CWaterRenderSystem__ReloadTextures", "void __fastcall CWaterRenderSystem__ReloadTextures(void * this, void * reload_target)"),
    "0x005524a0": ("CRenderQueue__UpdateViewVectorAndMatrix", "void __thiscall CRenderQueue__UpdateViewVectorAndMatrix(void * this, float x, float y, float z, int flags)"),
}

EXPECTED_XREFS = {
    "xrefs.tsv": {
        "0x00449ef0": {("0x0053e360", "CDXEngine__Render", "UNCONDITIONAL_CALL"), ("0x004685c4", "CFrontEnd__UpdateCamera", "UNCONDITIONAL_CALL")},
        "0x0044a0d0": {("0x0053e320", "CDXEngine__Render", "UNCONDITIONAL_CALL"), ("0x00487a0a", "CHud__RenderOverlayForViewpoint", "UNCONDITIONAL_CALL")},
        "0x0044a110": {("0x0043f4a1", "CCutscene__Stop", "UNCONDITIONAL_CALL")},
        "0x0044a130": {("0x0046ddf0", "CGame__RestartLoopRunLevel", "UNCONDITIONAL_CALL")},
        "0x0044a1f0": {("0x00491116", "CHeightField__DeserializeMapAndInitResources", "UNCONDITIONAL_CALL")},
        "0x0044a2a0": {("0x004910f2", "CHeightField__DeserializeMapAndInitResources", "UNCONDITIONAL_CALL")},
        "0x0044a2c0": {("0x00491138", "CHeightField__DeserializeMapAndInitResources", "UNCONDITIONAL_CALL")},
        "0x0044a2d0": {("0x0053e5b8", "CDXEngine__Render", "UNCONDITIONAL_CALL")},
    },
    "context-xrefs.tsv": {
        "0x0044a020": {("0x0046e680", "CGame__Render", "UNCONDITIONAL_CALL"), ("0x0046e878", "CGame__Render", "UNCONDITIONAL_CALL")},
        "0x0044a1c0": {("0x0046f029", "CGame__MainLoop", "UNCONDITIONAL_CALL")},
        "0x00491060": {("0x0044a72f", "CEngine__Deserialize", "UNCONDITIONAL_CALL")},
        "0x0044a6e0": {("0x004d768d", "CResourceAccumulator__ReadResourceFile", "UNCONDITIONAL_CALL")},
        "0x0053e2e0": {("0x0046e68b", "CGame__Render", "UNCONDITIONAL_CALL")},
        "0x005441a0": {("0x0044a2ab", "CEngine__SetKempyCube", "UNCONDITIONAL_CALL")},
        "0x00544fb0": {("0x0044a11d", "CEngine__ResetPos", "UNCONDITIONAL_CALL")},
        "0x0055b330": {("0x0044a2c8", "CEngine__SetWater", "UNCONDITIONAL_CALL")},
        "0x005524a0": {("0x0044a38e", "CEngine__SetupLights", "UNCONDITIONAL_CALL")},
    },
}

DECOMPILE_TOKENS = {
    "decompile/00449ef0_CEngine__GetViewMatrixFromCamera.c": ("1.570796", "outViewMatrix", "RET", "0x8"),
    "decompile/0044a0d0_CEngine__SelectViewpoint.c": ("0x4ac", "D3DDevice__SetViewport", "0x474"),
    "decompile/0044a110_CEngine__ResetPos.c": ("0x10", "CDXLandscape__ResetWrapper", "x,y"),
    "decompile/0044a130_CEngine__InitDamageSystem.c": ("CDamage__ResetDamageTables", "LockCurrentDamage-style", "tree-shadow"),
    "decompile/0044a1f0_CEngine__LoadMixers.c": ("0x49c", "CMapTex__LoadMixerTextureSet", "0x100", "0x1c8"),
    "decompile/0044a2a0_CEngine__SetKempyCube.c": ("0x498", "CDXEngine__InitKempyCubeResources", "number"),
    "decompile/0044a2c0_CEngine__SetWater.c": ("0x14", "CWaterRenderSystem__ReloadTextures", "number"),
    "decompile/0044a2d0_CEngine__SetupLights.c": ("MAP sun vector", "CRenderQueue__UpdateViewVectorAndMatrix", "DAT_009c7550"),
    "context-decompile/0053e2e0_CDXEngine__Render.c": ("CEngine__GetViewMatrixFromCamera", "D3DDevice__SetViewport", "CWaterRenderSystem__RenderMainPass", "CDXEngine__RenderKempyCubeFaces"),
    "context-decompile/005441a0_CDXEngine__InitKempyCubeResources.c": ("CDXEngine__InitKempyCubeTexturesAndVertexBuffer", "cube_index"),
    "context-decompile/00544fb0_CDXLandscape__ResetWrapper.c": ("CDXLandscape__Reset", "reset_x", "reset_y"),
    "context-decompile/0055b330_CWaterRenderSystem__ReloadTextures.c": ("CWaterRenderSystem__LoadTextures", "0x3ab8", "reload_target"),
    "context-decompile/005524a0_CRenderQueue__UpdateViewVectorAndMatrix.c": ("0x009c7550", "0x594", "0x6c4"),
}

CORE_TOKENS = (
    "Wave932",
    "cengine-view-resource-light-review-wave932",
    "130/1408 = 9.23%",
    "6113/6113 = 100.00%",
    BACKUP,
    "0x00449ef0 CEngine__GetViewMatrixFromCamera",
    "0x0044a0d0 CEngine__SelectViewpoint",
    "0x0044a110 CEngine__ResetPos",
    "0x0044a130 CEngine__InitDamageSystem",
    "0x0044a1f0 CEngine__LoadMixers",
    "0x0044a2a0 CEngine__SetKempyCube",
    "0x0044a2c0 CEngine__SetWater",
    "0x0044a2d0 CEngine__SetupLights",
    "0x0053e2e0 CDXEngine__Render",
    "0x005524a0 CRenderQueue__UpdateViewVectorAndMatrix",
    "no mutation",
)

OVERCLAIMS = (
    "runtime camera behavior proven",
    "runtime lighting behavior proven",
    "runtime water behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalize_address(value: str) -> str:
    text = value.strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return "0x" + text.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8-sig", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_counts_and_logs(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 8,
        "tags.tsv": 8,
        "xrefs.tsv": 11,
        "instructions.tsv": 403,
        "decompile/index.tsv": 8,
        "context-metadata.tsv": 9,
        "context-tags.tsv": 9,
        "context-xrefs.tsv": 19,
        "context-instructions.tsv": 963,
        "context-decompile/index.tsv": 9,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    expected_logs = {
        "metadata.log": "targets=8 found=8 missing=0",
        "tags.log": "rows=8 missing=0",
        "xrefs.log": "Wrote 11 rows",
        "instructions.log": "Wrote 403 function-body instruction rows",
        "decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "context-metadata.log": "targets=9 found=9 missing=0",
        "context-tags.log": "rows=9 missing=0",
        "context-xrefs.log": "Wrote 19 rows",
        "context-instructions.log": "Wrote 963 function-body instruction rows",
        "context-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_metadata(target_file: str, expected: dict[str, tuple[str, str]], failures: list[str]) -> None:
    rows = {normalize_address(row["address"]): row for row in read_tsv(BASE / target_file)}
    for address, (name, signature) in expected.items():
        row = rows.get(address)
        require(row is not None, f"missing metadata row {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch {address}", failures)
        require(row.get("signature") == signature, f"signature mismatch {address}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
        require(row.get("comment", "").strip(), f"missing comment {address}", failures)

    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / target_file.replace("metadata", "tags"))}
    for address in expected:
        row = tags.get(address)
        require(row is not None, f"missing tag row {address}", failures)
        if row is not None:
            require(row.get("status") == "OK", f"tag status mismatch {address}", failures)
            if address != "0x0053e2e0":
                require("static-reaudit" in row.get("tags", ""), f"missing static-reaudit tag {address}", failures)


def check_xrefs(failures: list[str]) -> None:
    for relative, expected_by_target in EXPECTED_XREFS.items():
        actual: dict[str, set[tuple[str, str, str]]] = {}
        for row in read_tsv(BASE / relative):
            key = normalize_address(row["target_addr"])
            actual.setdefault(key, set()).add((normalize_address(row["from_addr"]), row["from_function"], row["ref_type"]))
        for target, expected in expected_by_target.items():
            require(expected.issubset(actual.get(target, set())), f"xref mismatch for {target} in {relative}", failures)


def check_decompile_tokens(failures: list[str]) -> None:
    for relative, tokens in DECOMPILE_TOKENS.items():
        text = read_text(BASE / relative)
        require(text, f"missing decompile file {relative}", failures)
        for token in tokens:
            require(token in text, f"missing decompile token {relative}: {token}", failures)


def check_docs_and_state(failures: list[str]) -> None:
    package = json.loads(read_text(PACKAGE_JSON))
    require(package.get("scripts", {}).get(SCRIPT_NAME) == SCRIPT_VALUE, "missing package script", failures)

    for path in [NOTE, CAMPAIGN, ENGINE_DOC, *STATE_FILES]:
        text = read_text(path)
        require(text, f"missing doc/state file {path.relative_to(ROOT)}", failures)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    backup = json.loads(read_text(BASE / "backup-summary.json"))
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173247367, "backup bytes mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff mismatch", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_counts_and_logs(failures)
    check_metadata("metadata.tsv", TARGETS, failures)
    check_metadata("context-metadata.tsv", CONTEXT_TARGETS, failures)
    check_xrefs(failures)
    check_decompile_tokens(failures)
    check_docs_and_state(failures)

    if failures:
        print("Wave932 CEngine view/resource/light review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave932 CEngine view/resource/light review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
