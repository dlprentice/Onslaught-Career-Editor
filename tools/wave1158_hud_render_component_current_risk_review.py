#!/usr/bin/env python3
"""Validate Wave1158 HUD render/component current-risk review evidence."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1158-hud-render-component-current-risk-review"
FOCUSED_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.json"
RISK_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-risk-ranked-functions.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1158-hud-render-component-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1158-hud-render-component-current-risk-review.md"
CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "hud-frontend-overlay-static-contract.md"
CONTRACT_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "hud-frontend-overlay-static-contract.md"
READINESS = ROOT / "release" / "readiness" / "wave1158_hud_render_component_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260606-002152_post_wave1158_hud_render_component_current_risk_review_verified"
EXPECTED_SOURCE_ROOT = str(Path.home() / "Ghidra" / "Projects")

TARGETS = {
    "0x00481400": ("CHud__ctor_base", "void * __thiscall CHud__ctor_base(void * this)"),
    "0x00481450": ("CHud__Init", "void __thiscall CHud__Init(void * this)"),
    "0x004815c0": ("CHud__Reset", "void __thiscall CHud__Reset(void * this)"),
    "0x00481650": ("CHud__LoadTextures", "void __thiscall CHud__LoadTextures(void * this)"),
    "0x00481af0": ("CHud__PostLoadProcess", "int __thiscall CHud__PostLoadProcess(void * this)"),
    "0x00481b00": ("CHud__ShutDown", "void __thiscall CHud__ShutDown(void * this)"),
    "0x00481f40": ("CHud__SetHudComponent", "void __thiscall CHud__SetHudComponent(void * this, char * component_name, byte slot_flag)"),
    "0x00482050": ("CHud__PromotePendingHudComponent", "void __thiscall CHud__PromotePendingHudComponent(void * this)"),
    "0x00482210": ("CHud__RenderSegmentedMeterBar", "void __thiscall CHud__RenderSegmentedMeterBar(void * this, float x, float y, float width, float scale, float fill_fraction)"),
    "0x00482590": ("CHud__RenderTargetIndicatorOverlay", "void __thiscall CHud__RenderTargetIndicatorOverlay(void * this)"),
    "0x00483530": ("CHud__RenderControllerSlotStatusPanel", "void __thiscall CHud__RenderControllerSlotStatusPanel(void * this)"),
    "0x00484340": ("CHud__RenderTargetMarkers3D", "void __thiscall CHud__RenderTargetMarkers3D(void * this)"),
    "0x00484c50": ("CHud__RenderTacticalRadarContacts", "void __thiscall CHud__RenderTacticalRadarContacts(void * this)"),
    "0x004858d0": ("CHud__RenderObjectiveProgressGaugeAndHeadingNeedle", "void __thiscall CHud__RenderObjectiveProgressGaugeAndHeadingNeedle(void * this)"),
    "0x00485d50": ("CHud__RenderObjectiveStatusPanel", "void __thiscall CHud__RenderObjectiveStatusPanel(void * this)"),
    "0x00486940": ("CHud__RenderObjectiveSlotFillPanel", "void __thiscall CHud__RenderObjectiveSlotFillPanel(void * this)"),
    "0x00486e00": ("CHud__RenderWorldTargetSprites", "void __thiscall CHud__RenderWorldTargetSprites(void * this)"),
    "0x004879e0": ("CHud__RenderOverlayForViewpoint", "void __thiscall CHud__RenderOverlayForViewpoint(void * this, void * viewpoint, int viewpoint_index, float unused_overlay_param)"),
    "0x00487d10": ("CHud__RenderBattleline", "void __thiscall CHud__RenderBattleline(void * this, void * viewport)"),
    "0x00488090": ("CHud__RenderActiveHudComponentPass", "void __thiscall CHud__RenderActiveHudComponentPass(void * this)"),
}

EXPECTED_CALL_XREFS = {
    "0x00481400": {"0x00542743"},
    "0x00481450": {"0x0046c3d8"},
    "0x004815c0": {"0x0046c463"},
    "0x00481650": {"0x0046e367"},
    "0x00481af0": {"0x0046d052"},
    "0x00481b00": {"0x0046c9ac"},
    "0x00481f40": {"0x0043f505", "0x0043f3e8", "0x0043fa1f"},
    "0x00482050": {"0x0053ef5e"},
    "0x00482210": {"0x00483762", "0x004838e1", "0x004b8ad0"},
    "0x00482590": {"0x00487b72"},
    "0x00483530": {"0x00487b8a"},
    "0x00484340": {"0x00487b91"},
    "0x00484c50": {"0x00487bb2"},
    "0x004858d0": {"0x00487b98"},
    "0x00485d50": {"0x00487b9f"},
    "0x00486940": {"0x00487ba6"},
    "0x00486e00": {"0x00487b6b"},
    "0x004879e0": {"0x00487c57"},
    "0x00487d10": {"0x0053ed79"},
    "0x00488090": {"0x0053ef26"},
}

COMMON_TAGS = {"static-reaudit", "retail-binary-evidence", "hud"}

DOCS = [
    NOTE,
    NOTE_MIRROR,
    CONTRACT,
    CONTRACT_MIRROR,
    READINESS,
    PROGRESS,
    PROGRESS_MIRROR,
    ROOT / "README.md",
    ROOT / "CURRENT_CAPABILITIES.md",
    ROOT / "AGENTS.md",
    ROOT / "reverse-engineering" / "RE-INDEX.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Hud.cpp" / "_index.md",
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

DOC_TOKENS = (
    "Wave1158",
    "wave1158-hud-render-component-current-risk-review",
    "485/1179 = 41.14%",
    "20 HUD render/component current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 694",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "Codex read-only consults used",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "24 xref rows",
    "7335 instruction rows",
    "CHud__RenderOverlayForViewpoint",
    "CHud__RenderBattleline",
    "CHud__RenderActiveHudComponentPass",
    "CHud__RenderTacticalRadarContacts",
    "CHud__RenderObjectiveStatusPanel",
    "CHud__SetHudComponent",
    BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime hud behavior proven",
    "visible hud output proven",
    "rebuild parity proven",
    "exact layout proven",
    "source identity proven",
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
        "pre-metadata.tsv": 20,
        "pre-tags.tsv": 20,
        "pre-xrefs.tsv": 24,
        "pre-instructions.tsv": 7335,
        "pre-decompile/index.tsv": 20,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")

    xrefs_by_target: dict[str, list[dict[str, str]]] = {}
    for row in xrefs:
        xrefs_by_target.setdefault(normalize_address(row.get("target_addr", "")), []).append(row)

    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in ("Static retail", "runtime", "rebuild parity"):
                require(token in comment, f"missing comment boundary token at {address}: {token}", failures)

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

        actual_calls = {normalize_address(xref.get("from_addr", "")) for xref in xrefs_by_target.get(address, []) if xref.get("ref_type") == "UNCONDITIONAL_CALL"}
        require(EXPECTED_CALL_XREFS[address].issubset(actual_calls), f"call xrefs missing at {address}", failures)

    actual_ref_types = {row.get("ref_type") for row in xrefs}
    require(actual_ref_types == {"UNCONDITIONAL_CALL"}, f"unexpected xref types: {actual_ref_types}", failures)


def check_logs_backup_queue(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=20 found=20 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=20 missing=0",
        "pre-xrefs.log": "Wrote 24 rows",
        "pre-instructions.log": "Wrote 7335 function-body instruction rows",
        "pre-decompile.log": "targets=20 dumped=20 missing=0 failed=0",
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
    require(int(backup.get("totalBytes")) == 175967111, "backup byte count mismatch", failures)
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
    require(latest.get("wave") == "Wave1158 HUD render/component current-risk review", "latest wave mismatch", failures)
    require(latest.get("tag") == "wave1158-hud-render-component-current-risk-review", "latest tag mismatch", failures)
    require(latest.get("backup") == BACKUP, "latest backup mismatch", failures)
    require(current.get("focusedReviewed") == 485, "progress focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "41.14%", "progress focused percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 694, "progress remaining mismatch", failures)
    require(current.get("liveFocusedCandidatesAfterLatestReview") == 1178, "progress live focused mismatch", failures)
    require(current.get("latestReviewWave") == "Wave1158 HUD render/component current-risk review", "progress latest review mismatch", failures)

    for path in DOCS:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1158 note mirror mismatch", failures)
    require(read_text(CONTRACT) == read_text(CONTRACT_MIRROR), "HUD contract mirror mismatch", failures)
    require(read_text(PROGRESS) == read_text(PROGRESS_MIRROR), "progress mirror mismatch", failures)
    require(
        read_json(PACKAGE_JSON).get("scripts", {}).get("test:wave1158-hud-render-component-current-risk-review")
        == r"py -3 tools\wave1158_hud_render_component_current_risk_review.py --check",
        "missing package script",
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
        print("Wave1158 HUD render/component current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1158 HUD render/component current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
