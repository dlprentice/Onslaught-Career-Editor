#!/usr/bin/env python3
"""Validate Wave931 CEngine lifecycle/resource read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave931-cengine-lifecycle-resource-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_cengine_lifecycle_resource_review_wave931_2026-05-27.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
PACKAGE_JSON = ROOT / "package.json"
STATE_FILES = [
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260527-235851_post_wave931_cengine_lifecycle_resource_review_verified"
SCRIPT_NAME = "test:ghidra-cengine-lifecycle-resource-review-wave931"
SCRIPT_VALUE = r"py -3 tools\ghidra_cengine_lifecycle_resource_review_wave931_probe.py --check"

TARGETS = {
    "0x00449820": ("CEngine__ctor", "void __fastcall CEngine__ctor(void * engine)"),
    "0x00449890": ("CEngine__Shutdown", "void __fastcall CEngine__Shutdown(void * engine)"),
    "0x004499d0": ("CEngine__Init", "int __fastcall CEngine__Init(void * engine)"),
    "0x00449d50": ("CEngine__InitResources", "void __fastcall CEngine__InitResources(void * engine)"),
    "0x00449dc0": ("CEngine__LoadAllNamedMeshes", "void __thiscall CEngine__LoadAllNamedMeshes(void * this, void * dataFile)"),
    "0x0044a6e0": ("CEngine__Deserialize", "void __thiscall CEngine__Deserialize(void * this, void * chunkReader)"),
}

CONTEXT_TARGETS = {
    "0x0044a020": ("CEngine__SetViewpoint", "void __thiscall CEngine__SetViewpoint(void * this, int viewpoint, void * camera, void * viewport, void * player)"),
    "0x0044a1c0": ("CEngine__UpdatePos", "void __thiscall CEngine__UpdatePos(void * this, void * camera)"),
    "0x00491060": ("CHeightField__DeserializeMapAndInitResources", "void __thiscall CHeightField__DeserializeMapAndInitResources(void * this, void * chunk_reader)"),
    "0x0053d5f0": ("CDXEngine__Init", "int __fastcall CDXEngine__Init(void * this)"),
    "0x0053d6d0": ("CDXEngine__InitResources", "void __fastcall CDXEngine__InitResources(void * this)"),
}

EXPECTED_XREFS = {
    "xrefs.tsv": {
        "0x00449820": {("0x0053d345", "<no_function>", "UNCONDITIONAL_CALL")},
        "0x00449890": {("0x0053d3e4", "CDXEngine__Shutdown", "UNCONDITIONAL_CALL"), ("0x005e4fc4", "<no_function>", "DATA")},
        "0x004499d0": {("0x0053d5f3", "CDXEngine__Init", "UNCONDITIONAL_CALL"), ("0x005db274", "<no_function>", "DATA")},
        "0x00449d50": {("0x0053d6d3", "CDXEngine__InitResources", "UNCONDITIONAL_CALL"), ("0x005db278", "<no_function>", "DATA")},
        "0x00449dc0": {("0x0050bc34", "CWorld__LoadWorld", "UNCONDITIONAL_CALL")},
        "0x0044a6e0": {("0x004d768d", "CResourceAccumulator__ReadResourceFile", "UNCONDITIONAL_CALL")},
    },
    "context-xrefs.tsv": {
        "0x0044a020": {("0x0046e680", "CGame__Render", "UNCONDITIONAL_CALL"), ("0x0046e878", "CGame__Render", "UNCONDITIONAL_CALL")},
        "0x0044a1c0": {("0x0046f029", "CGame__MainLoop", "UNCONDITIONAL_CALL")},
        "0x00491060": {("0x0044a72f", "CEngine__Deserialize", "UNCONDITIONAL_CALL")},
        "0x0053d5f0": {("0x0046c39f", "CGame__Init", "UNCONDITIONAL_CALL"), ("0x005e4fc8", "<no_function>", "DATA")},
        "0x0053d6d0": {("0x0046e335", "CGame__RunLevel", "UNCONDITIONAL_CALL"), ("0x005e4fcc", "<no_function>", "DATA")},
    },
}

DECOMPILE_TOKENS = {
    "decompile/00449820_CEngine__ctor.c": ("PTR_CEngine__Shutdown_005db270", "0x4a8", "0x49c", "0x4ac"),
    "decompile/00449890_CEngine__Shutdown.c": ("CScreenFx__ReleaseZoomTextures", "CMapTex__Reset", "CEngine__TrimVbIbPoolCapacitiesPow2", "0x49c"),
    "decompile/004499d0_CEngine__Init.c": ("CConsole__RegisterVariable", "s_cg_renderlandscape_00628b9c", "s_cg_drawpolybuckets_00628b60", "CWaterRenderSystem__ctor", "CScreenFx__InitZoomEffectCvar"),
    "decompile/00449d50_CEngine__InitResources.c": ("CScreenFx__LoadZoomTextures", "s_hilight_tga_00628cb0", "s_hiteffect_tga_00628ca0", "s_cloak_tga_00628c94", "CDXLandscape__LoadCloudShadowTexture"),
    "decompile/00449dc0_CEngine__LoadAllNamedMeshes.c": ("s_Loading_named_meshes_00628cbc", "CDXMemBuffer__Read", "stricmp", "CMesh__FindOrCreate", "DAT_0089cdcc"),
    "decompile/0044a6e0_CEngine__Deserialize.c": ("CChunkReader__GetNext", "CChunkReader__Read", "CMapTex__Deserialize", "0x49c", "CHeightField__DeserializeMapAndInitResources"),
    "context-decompile/0044a020_CEngine__SetViewpoint.c": ("CInterpolatedCamera__ctor", "viewport", "player", "Source-aligned with engine.cpp::CEngine::SetViewpoint"),
    "context-decompile/0044a1c0_CEngine__UpdatePos.c": ("0x4a8", "0x10", "0x4ac", "CDXLandscape__SetTileData"),
    "context-decompile/00491060_CHeightField__DeserializeMapAndInitResources.c": ("CHeightField__Load", "CMixerMap__Init", "CEngine__LoadMixers", "Deserializing_map"),
    "context-decompile/0053d5f0_CDXEngine__Init.c": ("CEngine__Init", "SetGammaBias", "CDXPatchManager", "0x005e4fc8"),
    "context-decompile/0053d6d0_CDXEngine__InitResources.c": ("CEngine__InitResources", "s_meshtex_default_tga_00625498", "s_meshtex_outline_tga_006505e8", "s_default_msh_00632b30", "Sun_Sprite"),
}

CORE_TOKENS = (
    "Wave931",
    "cengine-lifecycle-resource-review-wave931",
    "122/1408 = 8.66%",
    "6113/6113 = 100.00%",
    BACKUP,
    "0x00449820 CEngine__ctor",
    "0x00449890 CEngine__Shutdown",
    "0x004499d0 CEngine__Init",
    "0x00449d50 CEngine__InitResources",
    "0x00449dc0 CEngine__LoadAllNamedMeshes",
    "0x0044a6e0 CEngine__Deserialize",
    "0x0044a020 CEngine__SetViewpoint",
    "0x0044a1c0 CEngine__UpdatePos",
    "0x00491060 CHeightField__DeserializeMapAndInitResources",
    "0x0053d5f0 CDXEngine__Init",
    "0x0053d6d0 CDXEngine__InitResources",
    "no mutation",
)

OVERCLAIMS = (
    "runtime engine boot proven",
    "runtime resource loading proven",
    "runtime render behavior proven",
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
        "metadata.tsv": 6,
        "tags.tsv": 6,
        "xrefs.tsv": 10,
        "instructions.tsv": 555,
        "decompile/index.tsv": 6,
        "context-metadata.tsv": 5,
        "context-tags.tsv": 5,
        "context-xrefs.tsv": 13,
        "context-instructions.tsv": 223,
        "context-decompile/index.tsv": 5,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    expected_logs = {
        "metadata.log": "targets=6 found=6 missing=0",
        "tags.log": "rows=6 missing=0",
        "xrefs.log": "Wrote 10 rows",
        "instructions.log": "Wrote 555 function-body instruction rows",
        "decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "context-metadata.log": "targets=5 found=5 missing=0",
        "context-tags.log": "rows=5 missing=0",
        "context-xrefs.log": "Wrote 13 rows",
        "context-instructions.log": "Wrote 223 function-body instruction rows",
        "context-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
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
        print("Wave931 CEngine lifecycle/resource review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave931 CEngine lifecycle/resource review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
