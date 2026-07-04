#!/usr/bin/env python3
"""Validate Wave923 HUD/radar/pause render read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave923-hud-radar-pause-render-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_hud_radar_pause_render_review_wave923_2026-05-27.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
PACKAGE_JSON = ROOT / "package.json"
STATE_FILES = [
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]
DOCS = [
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Hud.cpp" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "RadarWarningReceiver.cpp" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "PauseMenu.cpp" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ParticleDescriptor.cpp" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "d3dapp.cpp" / "_index.md",
]

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260527-210516_post_wave923_hud_radar_pause_render_review_verified"
SCRIPT_NAME = "test:ghidra-hud-radar-pause-render-review-wave923"
SCRIPT_VALUE = r"py -3 tools\ghidra_hud_radar_pause_render_review_wave923_probe.py --check"

TARGETS = {
    "0x00487d10": "CHud__RenderBattleline",
    "0x004d66b0": "CRadarWarningReceiver__Update",
    "0x004d15d0": "CPauseMenu__VFunc_03_HandleMenuControlInput",
    "0x004c14f0": "CPDSimpleSprite__VFunc_10_004c14f0",
    "0x004c8040": "CPDSimpleSprite__VFunc_23_004c8040",
    "0x0052a830": "CD3DApplication__FindDepthStencilFormat",
}

CORE_TOKENS = (
    "Wave923",
    "hud-radar-pause-render-review-wave923",
    "86/1408 = 6.11%",
    "6113/6113 = 100.00%",
    BACKUP,
)


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8-sig", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def normalized(addr: str) -> str:
    value = (addr or "").lower().strip()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def row_by_addr(rows: list[dict[str, str]], addr: str) -> dict[str, str]:
    want = normalized(addr)
    for row in rows:
        got = row.get("address") or row.get("target_addr") or row.get("function_entry") or ""
        if normalized(got) == want:
            return row
    return {}


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def build_report() -> dict[str, object]:
    failures: list[str] = []
    metadata = read_tsv(BASE / "metadata.tsv")
    tags = read_tsv(BASE / "tags.tsv")
    xrefs = read_tsv(BASE / "xrefs.tsv")
    instructions = read_tsv(BASE / "instructions.tsv")
    decomp = read_tsv(BASE / "decompile" / "index.tsv")
    summary = json.loads(read_text(BASE / "wave923-hud-radar-pause-render-review.json") or "{}")
    backup = json.loads(read_text(BASE / "backup-summary.json") or "{}")

    require(len(metadata) == 6, "metadata row count mismatch", failures)
    require(len(tags) == 6, "tag row count mismatch", failures)
    require(len(xrefs) == 6, "xref row count mismatch", failures)
    require(len(instructions) == 1009, "instruction row count mismatch", failures)
    require(len(decomp) == 6, "decompile row count mismatch", failures)

    for addr, name in TARGETS.items():
        mrow = row_by_addr(metadata, addr)
        require(mrow.get("name") == name, f"metadata name mismatch for {addr}", failures)
        require(mrow.get("status") == "OK", f"metadata status mismatch for {addr}", failures)
        drow = row_by_addr(decomp, addr)
        require(drow.get("name") == name, f"decompile name mismatch for {addr}", failures)
        require(drow.get("status") == "OK", f"decompile status mismatch for {addr}", failures)
        tag_text = row_by_addr(tags, addr).get("tags", "")
        require("static-reaudit" in tag_text, f"missing static-reaudit tag for {addr}", failures)

    require(summary.get("selectedTargets") == 6, "summary target count mismatch", failures)
    require(summary.get("mutatedTargets") == 0, "summary mutation count mismatch", failures)
    require(summary.get("focusedReauditProgressAfter") == "6.11%", "focused progress mismatch", failures)
    require(summary.get("reviewedFocusedCandidatesAfter") == 86, "focused reviewed count mismatch", failures)

    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", -1)) == 173247367, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)

    docs_to_check = [NOTE, CAMPAIGN, *STATE_FILES, *DOCS]
    for path in docs_to_check:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"{path.relative_to(ROOT)} missing {token}", failures)
    for addr, name in TARGETS.items():
        needle = f"{addr} {name}"
        combined_docs = "\n".join(read_text(path) for path in [NOTE, CAMPAIGN, *DOCS, *STATE_FILES])
        require(needle in combined_docs or name in combined_docs, f"missing target token {needle}", failures)

    package = json.loads(read_text(PACKAGE_JSON) or "{}")
    require(package.get("scripts", {}).get(SCRIPT_NAME) == SCRIPT_VALUE, "package script mismatch", failures)

    return {
        "schema": "ghidra-hud-radar-pause-render-review-wave923.probe.v1",
        "status": "PASS" if not failures else "FAIL",
        "targets": TARGETS,
        "mutatedTargets": 0,
        "instructionRows": len(instructions),
        "focusedReauditProgress": "86/1408 = 6.11%",
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=BASE / "wave923-probe-report.json")
    args = parser.parse_args()
    report = build_report()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Ghidra Wave923 HUD/radar/pause render review probe")
    print("Status:", report["status"])
    print("Output:", args.out.relative_to(ROOT))
    for failure in report["failures"]:
        print("-", failure)
    if args.check and report["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
