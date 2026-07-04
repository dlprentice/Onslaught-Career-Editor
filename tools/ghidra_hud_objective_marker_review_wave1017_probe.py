#!/usr/bin/env python3
"""Validate Wave1017 HUD objective/marker read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1017-hud-objective-marker-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_hud_objective_marker_review_wave1017_2026-05-31.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1017_recheck_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
HUD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Hud.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
TRACKING_STATE = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUALITY_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
RISK_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave911-risk-rank" / "wave911-risk-ranked-functions.tsv"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260531-201957_post_wave1017_hud_objective_marker_review_verified"

TARGETS = {
    "0x00484340": ("CHud__RenderTargetMarkers3D", "void __thiscall CHud__RenderTargetMarkers3D(void * this)"),
    "0x004858d0": (
        "CHud__RenderObjectiveProgressGaugeAndHeadingNeedle",
        "void __thiscall CHud__RenderObjectiveProgressGaugeAndHeadingNeedle(void * this)",
    ),
    "0x00486940": ("CHud__RenderObjectiveSlotFillPanel", "void __thiscall CHud__RenderObjectiveSlotFillPanel(void * this)"),
}

CONTEXT_TARGETS = {
    "0x00482590": "CHud__RenderTargetIndicatorOverlay",
    "0x00484c50": "CHud__RenderTacticalRadarContacts",
    "0x004857e0": "HudOverlay__DrawSpriteQuad",
    "0x00485830": "CHud__SelectMarkerTextureIndexByUnitFlags",
    "0x00485d50": "CHud__RenderObjectiveStatusPanel",
    "0x00486e00": "CHud__RenderWorldTargetSprites",
    "0x004879e0": "CHud__RenderOverlayForViewpoint",
    "0x00487bc0": "CHud__RenderOverlay",
    "0x00488090": "CHud__RenderActiveHudComponentPass",
    "0x004881e0": "CHud__ResolveOverlaySlotRenderMode",
    "0x0053ecc0": "CDXEngine__PostRender",
}

TARGET_COMMENT_TOKENS = {
    "0x00484340": ("Wave411 owner/signature correction", "CHud overlay helper", "CBattleEngine__GetInterpolatedAutoAimPos"),
    "0x004858d0": ("Wave411 owner/signature correction", "objective progress gauge", "CBattleEngine__GetWeaponCharge"),
    "0x00486940": ("Wave411 owner/signature correction", "weapon energy/ammo slot fill panel", "CBattleEngine__GetWeaponAmmoPercentage"),
}

TARGET_TAG_TOKENS = {
    "0x00484340": ("hud", "hud-overlay-helpers-wave411", "target-markers"),
    "0x004858d0": ("hud", "hud-overlay-helpers-wave411", "objective"),
    "0x00486940": ("hud", "hud-overlay-helpers-wave411", "weapon-status"),
}

DOC_TOKENS = (
    "Wave1017",
    "hud-objective-marker-review-wave1017",
    "0x00484340 CHud__RenderTargetMarkers3D",
    "0x004858d0 CHud__RenderObjectiveProgressGaugeAndHeadingNeedle",
    "0x00486940 CHud__RenderObjectiveSlotFillPanel",
    "0x004879e0 CHud__RenderOverlayForViewpoint",
    "513/1408 = 36.43%",
    "742/1493 = 49.70%",
    "442/500 = 88.40%",
    "6238/6238 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime hud behavior proven",
    "visible render ordering proven",
    "exact source-body identity proven",
    "exact layout proven",
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


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def rows_by(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    return {normalize_address(row.get(field, "")): row for row in rows}


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    normalized = text.replace("\\\\\\\\", "\\").replace("\\\\", "\\")
    return token in text or token.replace("\\", "\\\\") in text or token in normalized


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 3,
        "tags.tsv": 3,
        "xrefs.tsv": 3,
        "instructions.tsv": 1267,
        "decompile/index.tsv": 3,
        "context-metadata.tsv": 11,
        "context-xrefs.tsv": 26,
        "context-instructions.tsv": 4103,
        "context-decompile/index.tsv": 11,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = rows_by(read_tsv(BASE / "metadata.tsv"), "address")
    tags = rows_by(read_tsv(BASE / "tags.tsv"), "address")
    decompile = rows_by(read_tsv(BASE / "decompile" / "index.tsv"), "address")
    for address, (name, signature) in TARGETS.items():
        key = normalize_address(address)
        row = metadata.get(key)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            for token in TARGET_COMMENT_TOKENS[address]:
                require(token in comment, f"missing comment token {address}: {token}", failures)

        tag_row = tags.get(key)
        require(tag_row is not None, f"missing tags {address}", failures)
        if tag_row:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            for token in TARGET_TAG_TOKENS[address]:
                require(token in actual_tags, f"missing tag {address}: {token}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)

        dec = decompile.get(key)
        require(dec is not None, f"missing decompile {address}", failures)
        if dec:
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

    xrefs = read_tsv(BASE / "xrefs.tsv")
    expected_xrefs = {
        "0x00484340": ("0x00487b91", "CHud__RenderOverlayForViewpoint"),
        "0x004858d0": ("0x00487b98", "CHud__RenderOverlayForViewpoint"),
        "0x00486940": ("0x00487ba6", "CHud__RenderOverlayForViewpoint"),
    }
    for row in xrefs:
        target = normalize_address(row["target_addr"])
        if target in expected_xrefs:
            source, function = expected_xrefs[target]
            require(normalize_address(row.get("from_addr", "")) == source, f"xref source mismatch {target}", failures)
            require(row.get("from_function") == function, f"xref function mismatch {target}", failures)
            require(row.get("ref_type") == "UNCONDITIONAL_CALL", f"xref type mismatch {target}", failures)

    context = rows_by(read_tsv(BASE / "context-metadata.tsv"), "address")
    context_decompile = rows_by(read_tsv(BASE / "context-decompile" / "index.tsv"), "address")
    for address, name in CONTEXT_TARGETS.items():
        row = context.get(normalize_address(address))
        require(row is not None, f"missing context metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"context name mismatch {address}: {row.get('name')}", failures)
            require(row.get("status") == "OK", f"context status mismatch {address}", failures)
        dec = context_decompile.get(normalize_address(address))
        require(dec is not None, f"missing context decompile {address}", failures)
        if dec:
            require(dec.get("status") == "OK", f"context decompile status mismatch {address}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected_log_tokens = {
        "metadata.log": "targets=3 found=3 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=3 missing=0",
        "xrefs.log": "Wrote 3 rows",
        "instructions.log": "Wrote 1267 function-body instruction rows",
        "decompile.log": "targets=3 dumped=3 missing=0 failed=0",
        "context-metadata.log": "targets=11 found=11 missing=0",
        "context-xrefs.log": "Wrote 26 rows",
        "context-instructions.log": "Wrote 4103 function-body instruction rows",
        "context-decompile.log": "targets=11 dumped=11 missing=0 failed=0",
    }
    for relative, token in expected_log_tokens.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") in (173968263, 173968263.0), "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_queue_and_risk(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6238, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    quality_rows = rows_by(read_tsv(QUALITY_TSV), "address")
    risk_rows = rows_by(read_tsv(RISK_TSV), "address")
    expected_ranks = {"0x00484340": "345", "0x004858d0": "347", "0x00486940": "349"}
    for address, (name, signature) in TARGETS.items():
        qrow = quality_rows.get(address)
        require(qrow is not None, f"missing quality row {address}", failures)
        if qrow:
            require(qrow.get("name") == name, f"quality name mismatch {address}", failures)
            require(qrow.get("signature") == signature, f"quality signature mismatch {address}", failures)
            require(qrow.get("comment", "").strip(), f"quality comment missing {address}", failures)
        rrow = risk_rows.get(address)
        require(rrow is not None, f"missing risk row {address}", failures)
        if rrow:
            require(rrow.get("score") == "16", f"risk score mismatch {address}", failures)
            require("runtime_deferred" in rrow.get("signals", ""), f"risk signal mismatch {address}", failures)
            require(expected_ranks[address], f"missing expected rank literal {address}", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        HUD_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
        TRACKING_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-hud-objective-marker-review-wave1017")
        == r"py -3 tools\ghidra_hud_objective_marker_review_wave1017_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1017-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1017 --check",
        "missing aggregate package script",
        failures,
    )

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1017 HUD objective marker review" for row in ledger), "missing Wave1017 ledger row", failures)
    require(
        any(row.get("task") == "Wave1017 HUD objective marker review" and row.get("attempt_id") == 20599 for row in attempts),
        "missing Wave1017 attempt row",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_queue_and_risk(failures)
    check_docs(failures)

    if failures:
        print("Wave1017 HUD objective marker review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1017 HUD objective marker review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
