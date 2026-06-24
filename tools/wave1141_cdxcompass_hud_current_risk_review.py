#!/usr/bin/env python3
"""Validate Wave1141 CDXCompass/HUD current-risk review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1141-cdxcompass-hud-current-risk-review"
FOCUSED_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.json"
RISK_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-risk-ranked-functions.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1141-cdxcompass-hud-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1141-cdxcompass-hud-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1141_cdxcompass_hud_current_risk_review_2026-06-05.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
WAVE1108_NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
WAVE1108_READINESS = ROOT / "release" / "readiness" / "wave1108_current_risk_rank_2026-06-04.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
HUD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Hud.cpp" / "_index.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"G:\GhidraBackups\BEA_20260605-145724_post_wave1141_cdxcompass_hud_current_risk_review_verified"
PRIOR_BACKUP = r"G:\GhidraBackups\BEA_20260605-142515_post_wave1140_motion_controller_current_risk_review_verified"

TARGETS = {
    "0x0053bd60": (
        "CDXCompass__InitFields",
        "void * __fastcall CDXCompass__InitFields(void * this)",
        ("Wave591 owner/signature correction", "CHud__Init", "this+0x3c00"),
    ),
    "0x0053be40": (
        "CDXCompass__Init",
        "void __fastcall CDXCompass__Init(void * this)",
        ("Signature/comment correction", "CByteSprite", "ring texture"),
    ),
    "0x0053c1d0": (
        "CDXCompass__BuildRingGeometry",
        "void __cdecl CDXCompass__BuildRingGeometry(void * vertices, int textureWidth, int textureHeight, int segmentCount, int thicknessPercent, float uvScale)",
        ("fills a compass ring vertex strip", "segment count", "UV scale"),
    ),
    "0x00427110": (
        "CDXCompass__LoadTextures",
        "void __fastcall CDXCompass__LoadTextures(void * this)",
        ("ThreatFlash", "DamageFlash", "CompassObjectiveMarker"),
    ),
    "0x00427190": (
        "CDXCompass__DestroyTextures",
        "void __fastcall CDXCompass__DestroyTextures(void * this)",
        ("releases the four compass texture references", "CHud__ShutDown"),
    ),
    "0x00427200": (
        "CDXCompass__Reset",
        "void __fastcall CDXCompass__Reset(void * this)",
        ("clears the compass render/state flag", "this+0x3c10"),
    ),
    "0x004821b0": (
        "CDXCompass__ApplyRenderStateModulate",
        "void __cdecl CDXCompass__ApplyRenderStateModulate(void)",
        ("Wave400 signature/comment correction", "render states 0x13/0x14 to 2/2"),
    ),
    "0x004821e0": (
        "CDXCompass__ApplyRenderStateAdditive",
        "void __cdecl CDXCompass__ApplyRenderStateAdditive(void)",
        ("Wave400 signature/comment correction", "render states 0x13/0x14 to 5/6"),
    ),
    "0x00481400": (
        "CHud__ctor_base",
        "void * __thiscall CHud__ctor_base(void * this)",
        ("Wave400 owner/signature/comment correction", "active-reader cells", "component/compass slots"),
    ),
    "0x00481450": (
        "CHud__Init",
        "void __thiscall CHud__Init(void * this)",
        ("allocates compass/BattleLine HUD subobjects", "CGame__Init"),
    ),
    "0x00481650": (
        "CHud__LoadTextures",
        "void __thiscall CHud__LoadTextures(void * this)",
        ("crosshair/radar/weapon/objective/speaker", "compass"),
    ),
    "0x00481b00": (
        "CHud__ShutDown",
        "void __thiscall CHud__ShutDown(void * this)",
        ("destroys compass textures", "BattleLine allocations"),
    ),
    "0x00482090": (
        "HudRenderState__ApplyOverlaySpriteState",
        "void __cdecl HudRenderState__ApplyOverlaySpriteState(void)",
        ("shared HUD/message/compass/battleline overlay", "render-state setup"),
    ),
}

EXPECTED_XREFS = {
    "0x0053bd60": ("0x0048149a", "CHud__Init", "UNCONDITIONAL_CALL"),
    "0x0053be40": ("0x00427106", "CDXCompass__InitMarkerArrays", "UNCONDITIONAL_CALL"),
    "0x0053c1d0": ("0x0053c0f3", "CDXCompass__Init", "UNCONDITIONAL_CALL"),
    "0x00427110": ("0x00481ad3", "CHud__LoadTextures", "UNCONDITIONAL_CALL"),
    "0x00427190": ("0x00481b1a", "CHud__ShutDown", "UNCONDITIONAL_CALL"),
    "0x00427200": ("0x0053bd63", "CDXCompass__InitFields", "UNCONDITIONAL_CALL"),
    "0x004821b0": ("0x0042722c", "CDXCompass__Render", "UNCONDITIONAL_CALL"),
    "0x004821e0": ("0x00427911", "CDXCompass__Render", "UNCONDITIONAL_CALL"),
    "0x00481400": ("0x00542743", "CDXEngine__InitLandscapeTextureTables", "UNCONDITIONAL_CALL"),
    "0x00481450": ("0x0046c3d8", "CGame__Init", "UNCONDITIONAL_CALL"),
    "0x00481650": ("0x0046e367", "CGame__RunLevel", "UNCONDITIONAL_CALL"),
    "0x00481b00": ("0x0046c9ac", "CGame__Shutdown", "UNCONDITIONAL_CALL"),
    "0x00482090": ("0x00427222", "CDXCompass__Render", "UNCONDITIONAL_CALL"),
}

DOC_TOKENS = (
    "Wave1141",
    "wave1141-cdxcompass-hud-current-risk-review",
    "251/1179 = 21.29%",
    "13 current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 928",
    "current risk candidates: 6166",
    "CDXCompass/HUD render-state current-risk cluster",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    BACKUP,
    PRIOR_BACKUP,
)

OVERCLAIM_TOKENS = (
    "runtime compass behavior proven",
    "runtime hud behavior proven",
    "runtime rendering behavior proven",
    "visual qa proven",
    "rebuild parity proven",
)


def normalize_address(address: str) -> str:
    value = (address or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


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
        "pre-metadata.tsv": 13,
        "pre-tags.tsv": 13,
        "pre-xrefs.tsv": 28,
        "pre-instructions.tsv": 1310,
        "pre-decompile/index.tsv": 13,
        "context-metadata.tsv": 27,
        "context-tags.tsv": 27,
        "context-xrefs.tsv": 45,
        "context-instructions.tsv": 8549,
        "context-decompile/index.tsv": 27,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

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
            for token in comment_tokens:
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require("static-reaudit" in actual_tags, f"missing static-reaudit tag at {address}", failures)
            require("retail-binary-evidence" in actual_tags, f"missing retail-binary-evidence tag at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        from_addr, from_function, ref_type = EXPECTED_XREFS[address]
        require(
            any(
                normalize_address(row.get("target_addr", "")) == address
                and normalize_address(row.get("from_addr", "")) == from_addr
                and row.get("from_function") == from_function
                and row.get("ref_type") == ref_type
                for row in xrefs
            ),
            f"missing expected xref for {address}",
            failures,
        )

    context = {normalize_address(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}
    for address in (
        "0x00427210",
        "0x004879e0",
        "0x00487bc0",
        "0x0053c2e0",
        "0x0053c510",
        "0x0053cd30",
    ):
        require(address in context, f"missing context metadata row {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=13 found=13 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=13 missing=0",
        "pre-xrefs.log": "Wrote 28 rows",
        "pre-instructions.log": "Wrote 1310 function-body instruction rows",
        "pre-decompile.log": "targets=13 dumped=13 missing=0 failed=0",
        "context-metadata.log": "targets=27 found=27 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=27 missing=0",
        "context-xrefs.log": "Wrote 45 rows",
        "context-instructions.log": "Wrote 8549 function-body instruction rows",
        "context-decompile.log": "targets=27 dumped=27 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "SCRIPT ERROR", "BADADDR", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_progress_backup(failures: list[str]) -> None:
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

    risk = read_json(RISK_JSON)
    focused = read_json(FOCUSED_JSON)
    require(risk.get("totalFunctions") == 6411, "current risk total mismatch", failures)
    require(risk.get("candidateFunctions") == 6166, "current risk candidate mismatch", failures)
    require(focused.get("candidateFunctions") == 1178, "focused candidate mismatch", failures)

    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(progress["latestWave"]["wave"] == "Wave1141 CDXCompass/HUD current-risk review", "progress latest wave mismatch", failures)
    require(progress["latestWave"]["backup"] == BACKUP, "progress latest backup mismatch", failures)
    require(progress["functionQuality"]["totalFunctions"] == 6411, "progress function total mismatch", failures)
    require(progress["functionQuality"]["strictCleanSignatureProxy"] == "6411/6411 = 100.00%", "progress strict proxy mismatch", failures)
    require(current["focusedReviewed"] == 251, "progress focused reviewed mismatch", failures)
    require(current["focusedReviewedPercent"] == "21.29%", "progress focused percent mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 928, "progress remaining mismatch", failures)
    require(current["broadRiskCandidates"] == 6166, "progress broad candidates mismatch", failures)
    require(current["liveFocusedCandidatesAfterLatestReview"] == 1178, "progress live focused mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 175967111, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        MAPPED_SYSTEMS,
        MAPPED_SYSTEMS_MIRROR,
        CAMPAIGN,
        WAVE1108_NOTE,
        WAVE1108_READINESS,
        BINARY_INDEX,
        RE_INDEX,
        FUNCTION_COVERAGE,
        FUNCTION_INDEX,
        HUD_DOC,
        PROGRESS,
        PROGRESS_MIRROR,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:wave1141-cdxcompass-hud-current-risk-review") == r"py -3 tools\wave1141_cdxcompass_hud_current_risk_review.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_progress_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1141 CDXCompass/HUD current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1141 CDXCompass/HUD current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
