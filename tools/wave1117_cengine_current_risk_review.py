#!/usr/bin/env python3
"""Validate Wave1117 CEngine current-risk review."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
from pathlib import Path

import wave1108_current_risk_rank


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1117-cengine-current-risk-review"
FOCUSED_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.tsv"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1117-cengine-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1117-cengine-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1117_cengine_current_risk_review_2026-06-05.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
ENGINE_DOC_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"G:\GhidraBackups\BEA_20260605-014214_post_wave1117_cengine_current_risk_review_verified"
PRIOR_BACKUP = r"G:\GhidraBackups\BEA_20260605-011935_post_wave1116_door_wing_ai_current_risk_review_verified"

PRIOR_PROBES = (
    "wave1109_cfastvb_current_risk_head_supersession.py",
    "wave1110_cfastvb_wave1053_remainder_supersession.py",
    "wave1111_cnamedmesh_current_risk_supersession.py",
    "wave1112_animal_wave1016_current_risk_supersession.py",
    "wave1113_battleengine_wave936_wave1010_current_risk_supersession.py",
    "wave1114_mixed_score27_current_risk_head_supersession.py",
    "wave1115_unitai_carver_motion_activation_current_risk_review.py",
    "wave1116_door_wing_ai_current_risk_review.py",
)

TARGETS = {
    "0x00449820": ("CEngine__ctor", "void __fastcall CEngine__ctor(void * engine)", ("constructor", "+0x4a8", "near/far clip"), ("0x0053d345", "<no_function>", "UNCONDITIONAL_CALL"), ("PTR_CEngine__Shutdown_005db270", "0x430", "0x434", "0x4a8")),
    "0x00449890": ("CEngine__Shutdown", "void __fastcall CEngine__Shutdown(void * engine)", ("shutdown", "screen effects", "VB/IB pool"), ("0x0053d3e4", "CDXEngine__Shutdown", "UNCONDITIONAL_CALL"), ("Screen", "CMapTex", "0x49c")),
    "0x004499d0": ("CEngine__Init", "int __fastcall CEngine__Init(void * engine)", ("cg_renderlandscape", "cg_drawpolybuckets", "returns 1/0"), ("0x0053d5f3", "CDXEngine__Init", "UNCONDITIONAL_CALL"), ("cg_renderlandscape", "cg_drawpolybuckets", "CWaterRenderSystem", "CMapTex")),
    "0x0044a0d0": ("CEngine__SelectViewpoint", "void __thiscall CEngine__SelectViewpoint(void * this, int viewpoint)", ("RET 0x4", "+0x4ac", "D3DDevice__SetViewport"), ("0x0053e320", "CDXEngine__Render", "UNCONDITIONAL_CALL"), ("0x4ac", "D3DDevice__SetViewport", "SetViewport")),
    "0x0044a130": ("CEngine__InitDamageSystem", "void __fastcall CEngine__InitDamageSystem(void * engine)", ("damage tables", "tree-shadow", "LockCurrentDamage"), ("0x0046ddf0", "CGame__RestartLoopRunLevel", "UNCONDITIONAL_CALL"), ("landscape", "damage", "tree")),
    "0x0044a1f0": ("CEngine__LoadMixers", "void __thiscall CEngine__LoadMixers(void * this, int set)", ("RET 0x4", "CMapTex__LoadMixerTextureSet", "+0x49c"), ("0x00491116", "CHeightField__DeserializeMapAndInitResources", "UNCONDITIONAL_CALL"), ("CMapTex__LoadMixerTextureSet", "0x49c", "0x1c8")),
    "0x0044a2a0": ("CEngine__SetKempyCube", "void __thiscall CEngine__SetKempyCube(void * this, int number)", ("RET 0x4", "+0x498", "KempyCube"), ("0x004910f2", "CHeightField__DeserializeMapAndInitResources", "UNCONDITIONAL_CALL"), ("0x498", "CDXEngine__InitKempyCubeResources", "RET")),
    "0x0044a2c0": ("CEngine__SetWater", "void __thiscall CEngine__SetWater(void * this, int number)", ("RET 0x4", "+0x14", "CWaterRenderSystem__ReloadTextures"), ("0x00491138", "CHeightField__DeserializeMapAndInitResources", "UNCONDITIONAL_CALL"), ("0x14", "CWaterRenderSystem__ReloadTextures", "RET")),
    "0x0044a6e0": ("CEngine__Deserialize", "void __thiscall CEngine__Deserialize(void * this, void * chunkReader)", ("RET 0x4", "CChunkReader", "ENGN"), ("0x004d768d", "CResourceAccumulator__ReadResourceFile", "UNCONDITIONAL_CALL"), ("CChunkReader", "ENGN", "MAP", "0x49c")),
    "0x0044a830": ("VFuncSlot_03_0044a830", "void __thiscall VFuncSlot_03_0044a830(void * this, void * source_vector3)", ("shared vtable-slot", "source_vector3", "Owner unresolved"), ("0x004d65a9", "CRadarWarningReceiver__Init", "UNCONDITIONAL_CALL"), ("source_vector3", "0x08", "0x10")),
}

DOC_TOKENS = (
    "Wave1117",
    "wave1117-cengine-current-risk-review",
    "87/1179 = 7.38%",
    "10 rows",
    "current focused candidates: 1179",
    "score-26 CEngine core head",
    "fresh read-only Ghidra export",
    "no mutation",
    BACKUP,
    PRIOR_BACKUP,
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime engine behavior proven",
    "runtime render behavior proven",
    "exact layout proven",
    "source-body identity proven",
    "rebuild parity proven",
    "fully reverse-engineered",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig", errors="replace").replace("\x00", "")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def normalize_address(address: str) -> str:
    value = (address or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def contains_token(text: str, token: str) -> bool:
    normalized = text.replace("\\\\\\\\", "\\").replace("\\\\", "\\")
    return token in text or token.replace("\\", "\\\\") in text or token in normalized


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def import_probe(path: Path):
    if str(TOOLS) not in sys.path:
        sys.path.insert(0, str(TOOLS))
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def extract_probe_addresses(module) -> set[str]:
    addresses: set[str] = set()
    for attr in ("TOP15", "REMAINDER", "TARGETS"):
        if not hasattr(module, attr):
            continue
        value = getattr(module, attr)
        if isinstance(value, dict):
            addresses.update(normalize_address(address) for address in value)
        elif isinstance(value, (list, tuple, set)):
            for item in value:
                if isinstance(item, str):
                    addresses.add(normalize_address(item))
                elif isinstance(item, (list, tuple)) and item and isinstance(item[0], str):
                    addresses.add(normalize_address(item[0]))
    if hasattr(module, "ADDRESS"):
        addresses.add(normalize_address(getattr(module, "ADDRESS")))
    return addresses


def prior_accounted_addresses() -> set[str]:
    accounted: set[str] = set()
    for name in PRIOR_PROBES:
        accounted.update(extract_probe_addresses(import_probe(TOOLS / name)))
    return accounted


def row_map(path: Path, key: str = "address") -> dict[str, dict[str, str]]:
    return {normalize_address(row.get(key, "")): row for row in read_tsv(path)}


def check_wave1108_head(failures: list[str]) -> None:
    wave1108_current_risk_rank.generate()
    rows = read_tsv(FOCUSED_TSV)
    accounted = prior_accounted_addresses()
    remaining = [row for row in rows if normalize_address(row.get("address", "")) not in accounted]
    require(len(rows) == 1179, "Wave1108 focused row count mismatch", failures)
    require(len(accounted) == 77, f"prior accounted count mismatch: {len(accounted)}", failures)
    require(len(remaining) == 1102, f"remaining focused count mismatch: {len(remaining)}", failures)
    require([normalize_address(row.get("address", "")) for row in remaining[:10]] == list(TARGETS), "Wave1117 targets are not the next ten unaccounted Wave1108 focused rows", failures)
    for row in remaining[:10]:
        require(row.get("score") == "26", f"Wave1108 score mismatch: {row.get('address')}", failures)


def check_exports(failures: list[str]) -> None:
    counts = {
        "metadata.tsv": 10,
        "tags.tsv": 10,
        "xrefs.tsv": 17,
        "instructions.tsv": 1370,
        "decompile/index.tsv": 10,
    }
    for relative, expected in counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)
    log_tokens = {
        "metadata.log": "targets=10 found=10 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "xrefs.log": "Wrote 17 rows",
        "instructions.log": "targets=10 missing=0",
        "decompile.log": "targets=10 dumped=10 missing=0 failed=0",
    }
    for relative, token in log_tokens.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "MISSING\t", "missing=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_target_rows(failures: list[str]) -> None:
    metadata = row_map(BASE / "metadata.tsv")
    tags = row_map(BASE / "tags.tsv")
    decompile = row_map(BASE / "decompile" / "index.tsv")
    xrefs = read_tsv(BASE / "xrefs.tsv")
    instructions = read_tsv(BASE / "instructions.tsv")
    queue = row_map(QUEUE_TSV)

    for address, expected in TARGETS.items():
        name, signature, comment_tokens, xref, decompile_tokens = expected
        for label, rows in (("metadata", metadata), ("current queue", queue)):
            row = rows.get(address)
            require(row is not None, f"{label} missing: {address}", failures)
            if row is not None:
                require(row.get("name") == name, f"{label} name mismatch at {address}", failures)
                require(row.get("signature") == signature, f"{label} signature mismatch at {address}", failures)
                require(row.get("status") == "OK", f"{label} status mismatch at {address}", failures)
                for token in comment_tokens:
                    require(token in row.get("comment", ""), f"{label} missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            require(tag_row.get("name") == name, f"tag name mismatch at {address}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("name") == name, f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)
            dec_text = read_text(BASE / "decompile" / f"{address[2:]}_{name}.c")
            for token in decompile_tokens:
                require(token in dec_text, f"missing decompile token at {address}: {token}", failures)

        xref_from, xref_function, xref_type = xref
        require(
            any(
                normalize_address(row.get("target_addr", "")) == address
                and normalize_address(row.get("from_addr", "")) == normalize_address(xref_from)
                and row.get("from_function") == xref_function
                and row.get("ref_type") == xref_type
                for row in xrefs
            ),
            f"missing expected xref for {address}",
            failures,
        )

    setwater_instructions = [
        (row.get("instruction_addr"), row.get("mnemonic"), row.get("operands"))
        for row in instructions
        if normalize_address(row.get("target_addr", "")) == "0x0044a2c0"
    ]
    require(("0x0044a2c0", "MOV", "EAX, dword ptr [ESP + 0x4]") in setwater_instructions, "SetWater missing stack-argument load", failures)
    require(("0x0044a2c7", "PUSH", "EAX") in setwater_instructions, "SetWater missing stack-argument push", failures)
    require(("0x0044a2cd", "RET", "0x4") in setwater_instructions, "SetWater missing RET 0x4 evidence", failures)


def check_backup(failures: list[str]) -> None:
    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 175541127, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs_and_state(failures: list[str]) -> None:
    docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        MAPPED_SYSTEMS,
        MAPPED_SYSTEMS_MIRROR,
        CAMPAIGN,
        BINARY_INDEX,
        RE_INDEX,
        ENGINE_DOC,
        ENGINE_DOC_MIRROR,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing doc token in {path.relative_to(ROOT)}: {token}", failures)
        for address, expected in TARGETS.items():
            token = f"{address} {expected[0]}"
            require(contains_token(text, token), f"missing target token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    progress = read_json(PROGRESS)
    mirror = read_json(PROGRESS_MIRROR)
    for label, data in (("progress", progress), ("progress mirror", mirror)):
        current = data["post100Reaudit"]["currentRiskRank"]
        require(data["latestWave"]["wave"] == "Wave1117 CEngine current-risk review", f"{label} latest wave mismatch", failures)
        require(data["latestWave"]["tag"] == "wave1117-cengine-current-risk-review", f"{label} latest tag mismatch", failures)
        require(data["latestWave"]["backup"] == BACKUP, f"{label} backup mismatch", failures)
        require(data["latestWave"]["artifactCommit"] == "939195d66a5e78014921c0b460c4d325b755d8e3", f"{label} artifact commit mismatch", failures)
        require(current["focusedReviewed"] == 87, f"{label} focused reviewed mismatch", failures)
        require(current["focusedReviewedPercent"] == "7.38%", f"{label} focused percent mismatch", failures)
        require(current["latestReviewTag"] == "wave1117-cengine-current-risk-review", f"{label} review tag mismatch", failures)

    package = read_json(PACKAGE_JSON)
    expected_script = r"py -3 tools\wave1117_cengine_current_risk_review.py --check"
    require(package["scripts"].get("test:wave1117-cengine-current-risk-review") == expected_script, "missing package script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_wave1108_head(failures)
    check_exports(failures)
    check_target_rows(failures)
    check_backup(failures)
    check_docs_and_state(failures)
    if failures:
        print("Wave1117 CEngine current-risk review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1117 CEngine current-risk review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
