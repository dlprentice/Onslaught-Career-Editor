#!/usr/bin/env python3
"""Validate Wave990 HUD battleline/objective overlay read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave990-hud-battleline-objective-overlay-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_hud_battleline_objective_overlay_wave990_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
HUD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Hud.cpp" / "_index.md"
DXBATTLELINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXBattleLine.cpp.md"
FEARGRID_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FearGrid.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260531-041618_post_wave990_hud_battleline_objective_overlay_verified"

TARGETS = {
    "0x0040dda0": ("CUnitAI__RefreshGridCooldownFromOccupiedCells", "void __thiscall CUnitAI__RefreshGridCooldownFromOccupiedCells(void * this)"),
    "0x00414cb0": ("CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices", "void __thiscall CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices(void * this)"),
    "0x0042da00": ("Input__UpdateCursorCenterWithWindowScale", "void __cdecl Input__UpdateCursorCenterWithWindowScale(bool recenterNow)"),
    "0x0044c720": ("CFearGrid__GetOccupancyAtWorldVector", "int __thiscall CFearGrid__GetOccupancyAtWorldVector(void * this, float vector_x, float vector_y, float vector_z, float vector_w)"),
    "0x00485d50": ("CHud__RenderObjectiveStatusPanel", "void __thiscall CHud__RenderObjectiveStatusPanel(void * this)"),
    "0x00487d10": ("CHud__RenderBattleline", "void __thiscall CHud__RenderBattleline(void * this, void * viewport)"),
    "0x004e6610": ("SharedState__IsTimer88PendingAndState7CZero", "bool __fastcall SharedState__IsTimer88PendingAndState7CZero(void * this)"),
    "0x0053b5f0": ("CDXBattleLine__AppendOverlayVertex", "void __thiscall CDXBattleLine__AppendOverlayVertex(void * this, float world_x, float world_y, uint color_rgb)"),
}

COMMON_WAVE_TAGS = {
    "static-reaudit",
    "hud-battleline-objective-overlay-review-wave990",
    "wave990-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "xref-verified",
}

DOC_TOKENS = (
    "Wave990",
    "hud-battleline-objective-overlay-review-wave990",
    "0x0040dda0 CUnitAI__RefreshGridCooldownFromOccupiedCells",
    "0x00414cb0 CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices",
    "0x0044c720 CFearGrid__GetOccupancyAtWorldVector",
    "0x00485d50 CHud__RenderObjectiveStatusPanel",
    "0x00487d10 CHud__RenderBattleline",
    "441/1408 = 31.32%",
    "517/1478 = 34.98%",
    "6222/6222 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime hud behavior proven",
    "runtime battleline behavior proven",
    "runtime objective-panel behavior proven",
    "exact layout proven",
    "source-body identity proven",
    "rebuild parity proven",
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


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def row_by_address(rows: list[dict[str, str]], address: str, field: str = "address") -> dict[str, str] | None:
    target = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(field, "")) == target:
            return row
    return None


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_path_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text or token.replace("\\", "\\\\\\\\") in text


def check_exports(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 8,
        "tags.tsv": 8,
        "xrefs.tsv": 13,
        "instructions.tsv": 1429,
        "decompile/index.tsv": 8,
        "post-metadata.tsv": 8,
        "post-tags.tsv": 8,
        "post-xrefs.tsv": 13,
        "post-instructions.tsv": 1429,
        "post-decompile/index.tsv": 8,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = read_tsv(BASE / "post-metadata.tsv")
    tags = read_tsv(BASE / "post-tags.tsv")
    decompile_index = read_tsv(BASE / "post-decompile" / "index.tsv")
    for address, (name, signature) in TARGETS.items():
        row = row_by_address(metadata, address)
        require(row is not None, f"metadata missing {address}", failures)
        if row:
            require(row.get("name") == name, f"metadata name mismatch {address}", failures)
            require(row.get("signature") == signature, f"metadata signature mismatch {address}", failures)
            require(row.get("comment", "").strip() != "", f"metadata comment missing {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
        dec = row_by_address(decompile_index, address)
        require(dec is not None, f"decompile missing {address}", failures)
        if dec:
            require(dec.get("name") == name, f"decompile name mismatch {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)
        tag_row = row_by_address(tags, address)
        require(tag_row is not None, f"tags missing {address}", failures)
        if tag_row:
            require(tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)

    for address in ("0x0040dda0", "0x00414cb0"):
        row = row_by_address(metadata, address)
        tag_row = row_by_address(tags, address)
        require(row is not None and "Wave990" in row.get("comment", ""), f"missing Wave990 comment {address}", failures)
        require(row is not None and "CFearGrid__GetOccupancyAtWorldVector" in read_text(BASE / "post-decompile" / "0040dda0_CUnitAI__RefreshGridCooldownFromOccupiedCells.c"), "missing CFearGrid calls in 0x0040dda0 decompile", failures)
        if tag_row:
            actual_tags = set(filter(None, tag_row.get("tags", "").split(";")))
            require(COMMON_WAVE_TAGS.issubset(actual_tags), f"missing Wave990 tags {address}: {COMMON_WAVE_TAGS - actual_tags}", failures)

    comment_0040 = row_by_address(metadata, "0x0040dda0").get("comment", "")
    require("CSquadNormal grids" not in comment_0040, "stale CSquadNormal grids text remains in saved 0x0040dda0 comment", failures)
    require("CExplosionInitThing" not in comment_0040, "stale CExplosionInitThing text remains in saved 0x0040dda0 comment", failures)

    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    expected_xrefs = (
        ("0x0040dda0", "0x004862af", "CHud__RenderObjectiveStatusPanel"),
        ("0x00414cb0", "0x00488071", "CHud__RenderBattleline"),
        ("0x0044c720", "0x0040ddf3", "CUnitAI__RefreshGridCooldownFromOccupiedCells"),
        ("0x0044c720", "0x0040de22", "CUnitAI__RefreshGridCooldownFromOccupiedCells"),
        ("0x004e6610", "0x00414d1c", "CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices"),
        ("0x0053b5f0", "0x00414ce2", "CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices"),
        ("0x0053b5f0", "0x00414d35", "CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices"),
    )
    for target, source, owner in expected_xrefs:
        require(
            any(
                normalize_address(row.get("target_addr", "")) == target
                and normalize_address(row.get("from_addr", "")) == source
                and row.get("from_function") == owner
                for row in xrefs
            ),
            f"missing xref {source} -> {target} from {owner}",
            failures,
        )


def check_logs_queue_backup(failures: list[str]) -> None:
    expected_logs = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=2 comment_only_updated=2 tags_added=19 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=2 skipped=0 comment_only_updated=2 tags_added=19 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=2 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=8 found=8 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "post-xrefs.log": "Wrote 13 rows",
        "post-instructions.log": "targets=8 missing=0",
        "post-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "BADNAME", "BADSIG", "BADCOMMENT", "BADTAGS", "FAIL:", "missing=1", "failed=1"):
            require(bad not in text, f"bad log token {relative}: {bad}", failures)

    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6222, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "queue commentless mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "queue undefined mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "queue param_N mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173837191 or backup.get("totalBytes") == 173837191.0, "backup bytes mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        HUD_DOC,
        DXBATTLELINE_DOC,
        FEARGRID_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_path_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-hud-battleline-objective-overlay-wave990")
        == r"py -3 tools\ghidra_hud_battleline_objective_overlay_wave990_probe.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_exports(failures)
    check_logs_queue_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave990 HUD battleline/objective overlay probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave990 HUD battleline/objective overlay probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
